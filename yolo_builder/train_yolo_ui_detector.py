"""
YOLO Nano Training Program for UI Element Detection
Includes comprehensive data augmentation for small datasets
"""

import os
import yaml
import shutil
from pathlib import Path
import albumentations as A
import cv2
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt


class YOLOUITrainer:
    """Training pipeline for YOLO Nano UI element detector"""
    
    def __init__(self, dataset_path="datasets/ui_elements", output_path="models"):
        self.dataset_path = Path(dataset_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(exist_ok=True, parents=True)
        
        # Class names for UI elements (40 classes total - 8 elements × 5 services)
        self.class_names = self.generate_class_names()
        
        # Augmentation pipeline for small datasets
        self.augmentation = self.create_augmentation_pipeline()
        
    def generate_class_names(self):
        """Generate class names for all services and UI elements"""
        services = ['Perplexity', 'Gemini', 'ChatGPT', 'Claude', 'Grok']
        elements = ['input_box', 'send_btn', 'processing_indicator', 'action_icons', 
                   'copy_btn', 'more_btn', 'delete_btn', 'confirm_btn']
        
        class_names = []
        for service in services:
            for element in elements:
                class_names.append(f"{service}_{element}")
        
        return class_names
    
    def create_augmentation_pipeline(self):
        """
        Create comprehensive augmentation pipeline for UI screenshots
        Designed for small datasets (10-50 images per class)
        """
        return A.Compose([
            # Geometric transformations
            A.ShiftScaleRotate(
                shift_limit=0.05,
                scale_limit=0.1,
                rotate_limit=2,
                border_mode=cv2.BORDER_CONSTANT,
                p=0.5
            ),
            
            # Brightness and contrast variations (common in different lighting)
            A.RandomBrightnessContrast(
                brightness_limit=0.2,
                contrast_limit=0.2,
                p=0.6
            ),
            
            # Color adjustments (different monitors/themes)
            A.HueSaturationValue(
                hue_shift_limit=10,
                sat_shift_limit=15,
                val_shift_limit=15,
                p=0.4
            ),
            
            # Simulate different screen resolutions
            A.OneOf([
                A.Blur(blur_limit=3, p=1.0),
                A.GaussianBlur(blur_limit=3, p=1.0),
                A.MotionBlur(blur_limit=3, p=1.0),
            ], p=0.3),
            
            # Noise (simulate compression artifacts)
            A.OneOf([
                A.GaussNoise(var_limit=(5.0, 20.0), p=1.0),
                A.ISONoise(color_shift=(0.01, 0.03), intensity=(0.1, 0.3), p=1.0),
            ], p=0.3),
            
            # Simulate different DPI settings
            A.RandomScale(scale_limit=0.15, p=0.4),
            
            # Perspective changes (viewing angle)
            A.Perspective(scale=(0.02, 0.05), p=0.3),
            
            # Simulate cursor/overlays
            A.CoarseDropout(
                max_holes=3,
                max_height=20,
                max_width=20,
                min_holes=1,
                min_height=5,
                min_width=5,
                fill_value=0,
                p=0.2
            ),
            
        ], bbox_params=A.BboxParams(
            format='yolo',
            label_fields=['class_labels'],
            min_visibility=0.3
        ))
    
    def augment_dataset(self, original_images_path, augmented_images_path, 
                       original_labels_path, augmented_labels_path, 
                       augmentation_factor=10):
        """
        Augment dataset to increase training samples
        
        Args:
            original_images_path: Path to original images
            augmented_images_path: Path to save augmented images
            original_labels_path: Path to original labels
            augmented_labels_path: Path to save augmented labels
            augmentation_factor: Number of augmented versions per original image
        """
        original_images_path = Path(original_images_path)
        augmented_images_path = Path(augmented_images_path)
        original_labels_path = Path(original_labels_path)
        augmented_labels_path = Path(augmented_labels_path)
        
        # Create output directories
        augmented_images_path.mkdir(exist_ok=True, parents=True)
        augmented_labels_path.mkdir(exist_ok=True, parents=True)
        
        # Copy original files first
        print("Copying original dataset...")
        for img_file in original_images_path.glob("*.jpg"):
            shutil.copy(img_file, augmented_images_path / img_file.name)
            
            label_file = original_labels_path / f"{img_file.stem}.txt"
            if label_file.exists():
                shutil.copy(label_file, augmented_labels_path / label_file.name)
        
        # Generate augmented versions
        print(f"Generating {augmentation_factor}x augmented versions...")
        image_files = list(original_images_path.glob("*.jpg"))
        total_images = len(image_files)
        
        for idx, img_file in enumerate(image_files, 1):
            print(f"Augmenting image {idx}/{total_images}: {img_file.name}")
            
            # Read image
            image = cv2.imread(str(img_file))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w = image.shape[:2]
            
            # Read labels (YOLO format: class_id x_center y_center width height)
            label_file = original_labels_path / f"{img_file.stem}.txt"
            bboxes = []
            class_labels = []
            
            if label_file.exists():
                with open(label_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 5:
                            class_id = int(parts[0])
                            x_center, y_center, width, height = map(float, parts[1:])
                            bboxes.append([x_center, y_center, width, height])
                            class_labels.append(class_id)
            
            # Generate augmented versions
            for aug_idx in range(augmentation_factor):
                try:
                    # Apply augmentation
                    augmented = self.augmentation(
                        image=image,
                        bboxes=bboxes,
                        class_labels=class_labels
                    )
                    
                    aug_image = augmented['image']
                    aug_bboxes = augmented['bboxes']
                    aug_labels = augmented['class_labels']
                    
                    # Save augmented image
                    aug_img_name = f"{img_file.stem}_aug_{aug_idx}.jpg"
                    aug_img_path = augmented_images_path / aug_img_name
                    aug_image_bgr = cv2.cvtColor(aug_image, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(str(aug_img_path), aug_image_bgr)
                    
                    # Save augmented labels
                    aug_label_name = f"{img_file.stem}_aug_{aug_idx}.txt"
                    aug_label_path = augmented_labels_path / aug_label_name
                    
                    with open(aug_label_path, 'w') as f:
                        for bbox, label in zip(aug_bboxes, aug_labels):
                            x_center, y_center, width, height = bbox
                            f.write(f"{label} {x_center} {y_center} {width} {height}\n")
                    
                except Exception as e:
                    print(f"  Warning: Augmentation {aug_idx} failed: {e}")
                    continue
        
        print(f"Augmentation complete! Total images: {len(list(augmented_images_path.glob('*.jpg')))}")
    
    def prepare_dataset_yaml(self, train_images_path, val_images_path, yaml_path):
        """
        Create YOLO dataset configuration file
        
        Args:
            train_images_path: Path to training images
            val_images_path: Path to validation images
            yaml_path: Output path for dataset.yaml
        """
        config = {
            'path': str(Path(train_images_path).parent.parent),
            'train': str(Path(train_images_path).relative_to(Path(train_images_path).parent.parent)),
            'val': str(Path(val_images_path).relative_to(Path(val_images_path).parent.parent)),
            'nc': len(self.class_names),
            'names': self.class_names
        }
        
        with open(yaml_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"Dataset config saved to: {yaml_path}")
        return yaml_path
    
    def train_model(self, dataset_yaml, epochs=100, batch_size=16, img_size=640):
        """
        Train YOLO Nano model
        
        Args:
            dataset_yaml: Path to dataset configuration file
            epochs: Number of training epochs
            batch_size: Training batch size
            img_size: Input image size
        """
        print("="*60)
        print("Starting YOLO Nano Training")
        print("="*60)
        
        # Initialize YOLO Nano model
        model = YOLO('yolov8n.pt')  # Start from pretrained nano model
        
        # Training configuration
        results = model.train(
            data=dataset_yaml,
            epochs=epochs,
            batch=batch_size,
            imgsz=img_size,
            patience=20,
            save=True,
            device='cpu',  # Change to 'cuda' or 0 if GPU available
            
            # Optimizations for small datasets
            augment=True,
            mosaic=1.0,
            mixup=0.2,
            copy_paste=0.1,
            
            # Learning rate scheduling
            lr0=0.01,
            lrf=0.01,
            
            # Regularization
            weight_decay=0.0005,
            
            # Class balancing
            cls=0.5,
            
            # Output
            project=str(self.output_path),
            name='yolo_nano_ui',
            exist_ok=True
        )
        
        print("="*60)
        print("Training Complete!")
        print("="*60)
        
        return model, results
    
    def validate_model(self, model_path, dataset_yaml):
        """
        Validate trained model
        
        Args:
            model_path: Path to trained model weights
            dataset_yaml: Path to dataset configuration
        """
        print("="*60)
        print("Validating Model")
        print("="*60)
        
        model = YOLO(model_path)
        results = model.val(data=dataset_yaml)
        
        print(f"\nValidation Results:")
        print(f"mAP50: {results.box.map50:.4f}")
        print(f"mAP50-95: {results.box.map:.4f}")
        
        return results
    
    def visualize_predictions(self, model_path, test_images_path, output_path, num_samples=5):
        """
        Visualize model predictions on test images
        
        Args:
            model_path: Path to trained model
            test_images_path: Path to test images
            output_path: Path to save visualization
            num_samples: Number of samples to visualize
        """
        model = YOLO(model_path)
        output_path = Path(output_path)
        output_path.mkdir(exist_ok=True, parents=True)
        
        test_images = list(Path(test_images_path).glob("*.jpg"))[:num_samples]
        
        for img_path in test_images:
            # Run inference
            results = model(str(img_path))
            
            # Plot results
            for idx, result in enumerate(results):
                plot = result.plot()
                
                # Save visualization
                output_file = output_path / f"{img_path.stem}_prediction.jpg"
                cv2.imwrite(str(output_file), plot)
                print(f"Saved prediction: {output_file}")


def main():
    """Main training pipeline"""
    
    # Configuration
    DATASET_PATH = "datasets/ui_elements"
    OUTPUT_PATH = "models"
    AUGMENTATION_FACTOR = 10  # Generate 10x augmented versions
    EPOCHS = 100
    BATCH_SIZE = 16
    
    print("="*60)
    print("YOLO Nano UI Element Detector Training Pipeline")
    print("="*60)
    
    # Initialize trainer
    trainer = YOLOUITrainer(DATASET_PATH, OUTPUT_PATH)
    
    # Step 1: Augment dataset
    print("\n[Step 1/4] Augmenting Dataset...")
    original_train_images = Path(DATASET_PATH) / "original" / "train" / "images"
    original_train_labels = Path(DATASET_PATH) / "original" / "train" / "labels"
    augmented_train_images = Path(DATASET_PATH) / "augmented" / "train" / "images"
    augmented_train_labels = Path(DATASET_PATH) / "augmented" / "train" / "labels"
    
    trainer.augment_dataset(
        original_train_images,
        augmented_train_images,
        original_train_labels,
        augmented_train_labels,
        augmentation_factor=AUGMENTATION_FACTOR
    )
    
    # Also augment validation set (with lower factor)
    print("\nAugmenting Validation Set...")
    original_val_images = Path(DATASET_PATH) / "original" / "val" / "images"
    original_val_labels = Path(DATASET_PATH) / "original" / "val" / "labels"
    augmented_val_images = Path(DATASET_PATH) / "augmented" / "val" / "images"
    augmented_val_labels = Path(DATASET_PATH) / "augmented" / "val" / "labels"
    
    trainer.augment_dataset(
        original_val_images,
        augmented_val_images,
        original_val_labels,
        augmented_val_labels,
        augmentation_factor=3  # Less augmentation for validation
    )
    
    # Step 2: Prepare dataset configuration
    print("\n[Step 2/4] Preparing Dataset Configuration...")
    dataset_yaml = Path(DATASET_PATH) / "dataset.yaml"
    trainer.prepare_dataset_yaml(
        augmented_train_images,
        augmented_val_images,
        dataset_yaml
    )
    
    # Step 3: Train model
    print("\n[Step 3/4] Training YOLO Nano Model...")
    model, results = trainer.train_model(
        dataset_yaml,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE
    )
    
    # Step 4: Validate and visualize
    print("\n[Step 4/4] Validation and Visualization...")
    best_model_path = Path(OUTPUT_PATH) / "yolo_nano_ui" / "weights" / "best.pt"
    
    if best_model_path.exists():
        trainer.validate_model(best_model_path, dataset_yaml)
        
        # Visualize predictions on validation set
        viz_output = Path(OUTPUT_PATH) / "visualizations"
        trainer.visualize_predictions(
            best_model_path,
            augmented_val_images,
            viz_output,
            num_samples=10
        )
    
    print("\n" + "="*60)
    print("Training Pipeline Complete!")
    print(f"Best model saved to: {best_model_path}")
    print("="*60)


if __name__ == "__main__":
    main()
