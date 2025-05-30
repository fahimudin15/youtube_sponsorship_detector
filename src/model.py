import torch
import torch.nn as nn
from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer
from typing import Dict, List, Tuple, Optional
import os
import json
from datetime import datetime
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

class SponsorshipDetector(nn.Module):
    def __init__(self, model_name: str = 'distilbert-base-uncased'):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(self.bert.config.hidden_size, 1)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs[0][:, 0]  # Use CLS token
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        return self.sigmoid(logits)

class ModelTrainer:
    def __init__(self, model_dir: str = "models/saved_models"):
        self.model_dir = model_dir
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = SponsorshipDetector().to(self.device)
        self.criterion = nn.BCELoss()
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=2e-5)
        self.tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
        
    def train(self, train_dataloader, val_dataloader, epochs: int = 3) -> Dict:
        """Train the model and return training metrics"""
        best_val_loss = float('inf')
        training_history = []
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            train_loss = 0
            for batch in train_dataloader:
                self.optimizer.zero_grad()
                
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(input_ids, attention_mask)
                loss = self.criterion(outputs.squeeze(), labels.float())
                
                loss.backward()
                self.optimizer.step()
                train_loss += loss.item()
            
            # Validation
            val_loss, val_metrics = self.evaluate(val_dataloader)
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self.save_model('best_model')
            
            # Record metrics
            epoch_metrics = {
                'epoch': epoch + 1,
                'train_loss': train_loss / len(train_dataloader),
                'val_loss': val_loss,
                **val_metrics
            }
            training_history.append(epoch_metrics)
            
        return training_history

    def evaluate(self, dataloader) -> Tuple[float, Dict]:
        """Evaluate the model and return loss and metrics"""
        self.model.eval()
        val_loss = 0
        predictions = []
        true_labels = []
        
        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(input_ids, attention_mask)
                loss = self.criterion(outputs.squeeze(), labels.float())
                val_loss += loss.item()
                
                predictions.extend((outputs.squeeze() > 0.5).cpu().numpy())
                true_labels.extend(labels.cpu().numpy())
        
        # Calculate metrics
        precision, recall, f1, _ = precision_recall_fscore_support(
            true_labels, predictions, average='binary'
        )
        accuracy = accuracy_score(true_labels, predictions)
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
        
        return val_loss / len(dataloader), metrics

    def predict(self, text_data: Dict) -> List[float]:
        """Make predictions on new data"""
        self.model.eval()
        with torch.no_grad():
            input_ids = text_data['input_ids'].to(self.device)
            attention_mask = text_data['attention_mask'].to(self.device)
            outputs = self.model(input_ids, attention_mask)
            return outputs.squeeze().cpu().numpy().tolist()

    def predict_segments(self, windows_data: List[Dict], threshold: float = 0.5) -> List[Dict]:
        """
        Make predictions on video segments and identify potential sponsorship regions
        Args:
            windows_data: List of windows with text and timestamp information
            threshold: Confidence threshold for sponsorship detection
        Returns:
            List of segments with predictions and confidence scores
        """
        self.model.eval()
        results = []
        
        # Process windows in batches
        batch_size = 8
        for i in range(0, len(windows_data), batch_size):
            batch = windows_data[i:i + batch_size]
            texts = [w['processed_text'] for w in batch]
            
            # Tokenize
            inputs = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            ).to(self.device)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(
                    inputs['input_ids'],
                    inputs['attention_mask']
                )
                predictions = outputs.squeeze().cpu().numpy()
            
            # Add results
            for j, window in enumerate(batch):
                confidence = float(predictions[j])
                results.append({
                    'start_time': window['start_time'],
                    'end_time': window['end_time'],
                    'confidence': confidence,
                    'is_sponsored': confidence > threshold
                })
        
        return results

    def save_model(self, model_name: str):
        """Save the model and its configuration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = os.path.join(self.model_dir, f"{model_name}_{timestamp}")
        os.makedirs(save_dir, exist_ok=True)
        
        # Save model state
        torch.save(self.model.state_dict(), os.path.join(save_dir, 'model.pt'))
        
        # Save model configuration
        config = {
            'model_type': 'SponsorshipDetector',
            'base_model': 'distilbert-base-uncased',
            'saved_at': timestamp
        }
        with open(os.path.join(save_dir, 'config.json'), 'w') as f:
            json.dump(config, f)

    def load_model(self, model_path: str):
        """Load a saved model"""
        self.model.load_state_dict(torch.load(os.path.join(model_path, 'model.pt')))
        self.model.eval()
