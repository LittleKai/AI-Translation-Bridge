import os
import pandas as pd


class PromptHelper:
    """Helper class for prompt and batch processing operations"""

    @staticmethod
    def detect_language(filepath):
        """Detect language from filename"""
        filename = os.path.basename(filepath)
        for lang in ['JP', 'EN', 'KR', 'CN', 'VI']:
            if lang in filename.upper():
                return lang
        return None

    @staticmethod
    def load_translation_prompt(input_path, prompt_type, log_func=None):
        """Load translation prompt based on detected language and prompt type"""
        source_lang = PromptHelper.detect_language(input_path)

        if not source_lang:
            if log_func:
                log_func("Error: Could not detect source language from filename")
                log_func("Filename should contain language code (CN, JP, EN, KR, VI)")
            return None

        if log_func:
            log_func(f"Loading prompt for source language: {source_lang}, type: {prompt_type}")

        try:
            prompt_file = "assets/translate_prompt.xlsx"
            if not os.path.exists(prompt_file):
                if log_func:
                    log_func("Error: Prompt file not found at assets/translate_prompt.xlsx")
                return None

            df = pd.read_excel(prompt_file)

            if 'type' in df.columns and source_lang in df.columns:
                prompt_row = df[df['type'] == prompt_type]
                if not prompt_row.empty:
                    prompt = prompt_row.iloc[0][source_lang]
                    if pd.notna(prompt) and prompt:
                        if log_func:
                            log_func(f"Successfully loaded prompt for {source_lang}, type: {prompt_type}")

                        prompt_with_format = prompt.strip() + "\n{count_info}\nVẫn giữ định dạng đánh số như bản gốc (1., 2., ...).\n" \
                                                              "Đây là văn bản cần chuyển ngữ:\n{text}"
                        # "Chỉ trả về các dòng dịch được đánh số, không viết thêm bất kỳ nội dung nào khác.\n" \ \
                        return prompt_with_format
                    else:
                        if log_func:
                            log_func(f"Error: Prompt is empty for {source_lang}, type: {prompt_type}")
                else:
                    if log_func:
                        log_func(f"Error: Prompt type '{prompt_type}' not found in file")
            else:
                if log_func:
                    if 'type' not in df.columns:
                        log_func("Error: 'type' column not found in prompt file")
                    if source_lang not in df.columns:
                        log_func(f"Error: Language column '{source_lang}' not found in prompt file")
                        available_langs = [col for col in df.columns if col not in ['type', 'description']]
                        log_func(f"Available languages: {', '.join(available_langs)}")

            return None

        except Exception as e:
            if log_func:
                log_func(f"Error loading prompt file: {e}")
            return None

    @staticmethod
    def generate_output_path(input_path, prompt_type):
        """Generate output path based on input file name and prompt type"""
        input_filename = os.path.basename(input_path)

        # Detect language from filename
        lang_folder = PromptHelper.detect_language(input_path)
        if not lang_folder:
            lang_folder = "Other"

        # Create output filename
        filename_without_ext, ext = os.path.splitext(input_filename)

        # Keep the same extension as input file if it's CSV or Excel
        output_ext = ext if ext.lower() in ['.csv', '.xlsx', '.xls'] else '.csv'

        if prompt_type:
            output_filename = f"{filename_without_ext}_{prompt_type}_translated{output_ext}"
        else:
            output_filename = f"{filename_without_ext}_translated{output_ext}"

        # Create output directory
        output_dir = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "AIBridge",
            "Translated",
            lang_folder
        )

        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, output_filename)

    @staticmethod
    def apply_id_filters(df, start_id, stop_id):
        """Apply start_id and stop_id filters to dataframe"""
        try:
            if start_id:
                start_id = int(start_id)
                df = df[df['id'] >= start_id]

            if stop_id:
                stop_id = int(stop_id)
                df = df[df['id'] <= stop_id]
        except:
            pass

        return df

    @staticmethod
    def create_batch_text(batch_df):
        """Create numbered text from batch dataframe"""
        batch_lines = []
        for j, (_, row) in enumerate(batch_df.iterrows(), 1):
            batch_lines.append(f"{j}. {row['text']}")
        return "\n".join(batch_lines)

    @staticmethod
    def save_results(existing_results, output_path):
        """Save results to CSV or Excel file based on extension"""
        if not existing_results:
            print(f"[ERROR] No results to save")
            return False

        try:
            results_list = list(existing_results.values())
            results_df = pd.DataFrame(results_list)
            results_df_sorted = results_df.sort_values('id')

            # Check output format by extension
            _, ext = os.path.splitext(output_path)
            ext = ext.lower()

            print(f"[DEBUG] Saving to {output_path} with extension: {ext}")

            if ext in ['.xlsx', '.xls']:
                try:
                    # Clean data before saving to Excel
                    print(f"[DEBUG] Preparing Excel data...")

                    # Clean columns
                    for col in results_df_sorted.columns:
                        if col != 'id':
                            # Replace NaN and convert to string
                            results_df_sorted[col] = results_df_sorted[col].fillna('')
                            results_df_sorted[col] = results_df_sorted[col].astype(str)

                    # Ensure id column is numeric
                    if 'id' in results_df_sorted.columns:
                        results_df_sorted['id'] = pd.to_numeric(results_df_sorted['id'], errors='coerce').fillna(0).astype(int)

                    print(f"[DEBUG] Writing Excel file with openpyxl...")

                    # Create directory if not exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    # Write Excel file
                    results_df_sorted.to_excel(
                        output_path,
                        index=False,
                        engine='openpyxl'
                    )

                    print(f"[SUCCESS] Excel file saved: {output_path}")
                    return True

                except Exception as e:
                    print(f"[ERROR] Failed to save Excel: {e}")
                    print(f"[ERROR] Full traceback:")
                    import traceback
                    traceback.print_exc()

                    # Fallback to CSV
                    csv_path = output_path.replace('.xlsx', '.csv').replace('.xls', '.csv')
                    print(f"[INFO] Falling back to CSV: {csv_path}")

                    try:
                        results_df_sorted.to_csv(csv_path, index=False, encoding='utf-8-sig')
                        print(f"[SUCCESS] CSV fallback saved: {csv_path}")
                        return True
                    except Exception as csv_error:
                        print(f"[ERROR] CSV fallback also failed: {csv_error}")
                        return False
            else:
                # Save as CSV
                results_df_sorted.to_csv(output_path, index=False, encoding='utf-8-sig')
                print(f"[SUCCESS] CSV file saved: {output_path}")
                return True

        except Exception as e:
            print(f"[ERROR] Unexpected error in save_results: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def load_existing_results(output_path, chunk_size=10000):
        """Load and analyze existing output file with optimization for large files"""
        existing_results = {}
        completed_ids = set()
        failed_ids = set()

        if os.path.exists(output_path):
            try:
                # Check file size
                file_size = os.path.getsize(output_path)
                is_large_file = file_size > 10 * 1024 * 1024  # > 10MB

                # Check file extension
                _, ext = os.path.splitext(output_path)
                ext = ext.lower()

                if ext in ['.xlsx', '.xls']:
                    existing_df = pd.read_excel(output_path, engine='openpyxl')
                else:
                    # For large CSV files, read in chunks
                    if is_large_file:
                        chunks = []
                        for chunk in pd.read_csv(output_path, chunksize=chunk_size, encoding='utf-8', encoding_errors='replace'):
                            chunks.append(chunk)
                        existing_df = pd.concat(chunks, ignore_index=True)
                    else:
                        existing_df = pd.read_csv(output_path, encoding='utf-8', encoding_errors='replace')

                if not existing_df.empty:
                    for _, row in existing_df.iterrows():
                        row_id = row['id']
                        existing_results[row_id] = {
                            'id': row_id,
                            'raw': row.get('raw', ''),
                            'edit': row.get('edit', ''),
                            'status': row.get('status', '')
                        }

                        # Check if translation exists and is valid
                        edit_value = row.get('edit', '')
                        if edit_value and str(edit_value).strip() and str(edit_value).strip() != 'nan':
                            completed_ids.add(row_id)
                        else:
                            failed_ids.add(row_id)
            except:
                pass

        return existing_results, completed_ids, failed_ids

    @staticmethod
    def find_next_batch(df, output_path, batch_size):
        """Find the next batch of IDs that need processing"""
        if df is None or df.empty:
            return None

        if batch_size <= 0:
            return None

        all_input_ids = set(df['id'].tolist())

        # Load existing results
        _, completed_ids, _ = PromptHelper.load_existing_results(output_path)

        # Find IDs to process
        ids_to_process = sorted(all_input_ids - completed_ids)

        if not ids_to_process:
            return None

        # Get next batch
        batch_ids = ids_to_process[:min(batch_size, len(ids_to_process))]
        batch_df = df[df['id'].isin(batch_ids)].sort_values('id')

        # Return a copy to ensure data persists
        return batch_df.copy() if not batch_df.empty else None

    @staticmethod
    def read_input_file(input_file, log_func=None):
        """Read input file (CSV or Excel) with proper encoding handling

        Args:
            input_file: Path to input file
            log_func: Optional logging function

        Returns:
            DataFrame if successful, None if failed
        """
        try:
            # Check file extension
            _, ext = os.path.splitext(input_file)
            ext = ext.lower()

            # Check file size for optimization
            file_size = os.path.getsize(input_file)
            is_large_file = file_size > 10 * 1024 * 1024  # > 10MB

            if is_large_file and log_func:
                log_func(f"Processing large file ({file_size / 1024 / 1024:.1f} MB)...")

            if ext in ['.xlsx', '.xls']:
                df = pd.read_excel(input_file, engine='openpyxl')
                if log_func:
                    log_func(f"Loaded {len(df)} rows from Excel file")
            else:
                # For large CSV files, use optimized reading
                if is_large_file:
                    dtype_dict = {'id': 'int32', 'text': 'str'}
                    df = pd.read_csv(input_file, dtype=dtype_dict, low_memory=False, encoding='utf-8')
                    if log_func:
                        log_func(f"Loaded {len(df)} rows from large CSV file")
                else:
                    df = pd.read_csv(input_file, encoding='utf-8')
                    if log_func:
                        log_func(f"Loaded {len(df)} rows from CSV file")

            # Validate required columns
            if 'id' not in df.columns:
                if log_func:
                    log_func("Error: File must have 'id' column")
                return None

            if 'text' not in df.columns:
                if log_func:
                    log_func("Error: File must have 'text' column")
                    log_func(f"Available columns: {', '.join(df.columns)}")
                return None

            return df

        except Exception as e:
            if log_func:
                log_func(f"Error reading input file: {e}")
            return None