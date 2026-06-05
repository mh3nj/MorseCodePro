import numpy as np
from typing import Dict, List

class ConfidenceScorer:
    def __init__(self):
        self.weights = {
            'signal_noise_ratio': 0.25,
            'timing_consistency': 0.20,
            'valid_characters': 0.30,
            'dah_dit_ratio': 0.15,
            'frequency_stability': 0.10
        }
    
    def score_detection(self, morse_code: str, 
                       audio_features: Dict = None) -> float:
        """Calculate confidence score for Morse detection"""
        scores = {}
        
        # 1. Signal-to-noise ratio score
        if audio_features and 'snr' in audio_features:
            snr = audio_features['snr']
            scores['signal_noise_ratio'] = min(1.0, snr / 20)  # 20dB = 100%
        else:
            scores['signal_noise_ratio'] = 0.7
        
        # 2. Timing consistency
        scores['timing_consistency'] = self._check_timing_consistency(morse_code)
        
        # 3. Valid characters in Morse
        scores['valid_characters'] = self._check_valid_characters(morse_code)
        
        # 4. Dah/dit ratio
        scores['dah_dit_ratio'] = self._check_dah_dit_ratio(morse_code)
        
        # 5. Frequency stability (if provided)
        scores['frequency_stability'] = audio_features.get('freq_stability', 0.7) if audio_features else 0.7
        
        # Calculate weighted score
        total_score = sum(
            scores[metric] * self.weights[metric] 
            for metric in scores
        )
        
        return round(total_score * 100, 1)  # Percentage
    
    def _check_timing_consistency(self, morse_code: str) -> float:
        """Check if timing between symbols is consistent"""
        symbols = []
        for char in morse_code:
            if char in ['.', '-']:
                symbols.append(char)
        
        if len(symbols) < 2:
            return 0.5
        
        # Count runs of same symbol
        runs = []
        current_run = 1
        for i in range(1, len(symbols)):
            if symbols[i] == symbols[i-1]:
                current_run += 1
            else:
                runs.append(current_run)
                current_run = 1
        runs.append(current_run)
        
        # Check variance in run lengths
        if len(runs) > 1:
            variance = np.var(runs)
            consistency = max(0, 1 - (variance / 10))
            return min(1.0, consistency)
        return 0.7
    
    def _check_valid_characters(self, morse_code: str) -> float:
        """Check if Morse code contains only valid symbols"""
        valid_chars = {'.', '-', ' ', '/'}
        total_chars = len(morse_code)
        if total_chars == 0:
            return 0
        
        valid_count = sum(1 for c in morse_code if c in valid_chars)
        return valid_count / total_chars
    
    def _check_dah_dit_ratio(self, morse_code: str) -> float:
        """Check if dah/dit ratio is approximately 3:1"""
        dits = morse_code.count('.')
        dahs = morse_code.count('-')
        
        if dits == 0 or dahs == 0:
            return 0.5
        
        ratio = (dahs * 3) / dits  # Expect ~1 for good signal
        if 0.7 <= ratio <= 1.3:
            return 1.0
        elif 0.4 <= ratio <= 1.6:
            return 0.7
        return 0.3
    
    def get_detailed_report(self, morse_code: str, 
                           audio_features: Dict = None) -> Dict:
        """Get detailed confidence breakdown"""
        scores = {}
        
        if audio_features and 'snr' in audio_features:
            scores['Signal-to-Noise Ratio'] = f"{audio_features['snr']:.1f} dB"
        
        scores['Timing Consistency'] = f"{self._check_timing_consistency(morse_code)*100:.0f}%"
        scores['Valid Characters'] = f"{self._check_valid_characters(morse_code)*100:.0f}%"
        scores['Dah/Dit Ratio'] = f"{self._check_dah_dit_ratio(morse_code)*100:.0f}%"
        
        total = self.score_detection(morse_code, audio_features)
        
        return {
            'breakdown': scores,
            'total': total,
            'quality': self._get_quality_label(total)
        }
    
    def _get_quality_label(self, score: float) -> str:
        """Get quality label based on score"""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Fair"
        elif score >= 30:
            return "Poor"
        else:
            return "Unreliable""""
Calculate confidence score for Morse code detection
"""

import numpy as np

class ConfidenceScorer:
    def __init__(self):
        self.score_weights = {
            'signal_clarity': 0.3,
            'timing_consistency': 0.25,
            'valid_characters': 0.25,
            'signal_to_noise': 0.2
        }
    
    def calculate_score(self, morse_code, audio_data=None, sample_rate=44100):
        """Calculate overall confidence score (0-100)"""
        scores = {}
        
        # 1. Valid characters score
        scores['valid_characters'] = self._check_valid_characters(morse_code)
        
        # 2. Timing consistency score
        scores['timing_consistency'] = self._check_timing_consistency(morse_code)
        
        # 3. Signal clarity (if audio provided)
        if audio_data is not None:
            scores['signal_clarity'] = self._check_signal_clarity(audio_data)
            scores['signal_to_noise'] = self._calculate_snr(audio_data)
        else:
            scores['signal_clarity'] = 0.7
            scores['signal_to_noise'] = 0.7
        
        # Calculate weighted score
        total_score = sum(
            scores[metric] * self.score_weights.get(metric, 0.25)
            for metric in scores
        )
        
        return {
            'total': round(total_score * 100, 1),
            'breakdown': {k: round(v * 100, 1) for k, v in scores.items()},
            'quality': self._get_quality_label(total_score * 100)
        }
    
    def _check_valid_characters(self, morse_code):
        """Check percentage of valid Morse characters"""
        valid_chars = {'.', '-', ' ', '/'}
        if not morse_code:
            return 0
        
        valid_count = sum(1 for c in morse_code if c in valid_chars)
        return valid_count / len(morse_code)
    
    def _check_timing_consistency(self, morse_code):
        """Check if timing between symbols is consistent"""
        symbols = [c for c in morse_code if c in ['.', '-']]
        if len(symbols) < 2:
            return 0.5
        
        # Check for reasonable dit/dah ratio
        dits = symbols.count('.')
        dahs = symbols.count('-')
        
        if dits == 0 or dahs == 0:
            return 0.6
        
        ratio = dahs / dits
        if 0.3 <= ratio <= 0.7:  # Expected ratio in good Morse
            return 0.9
        elif 0.2 <= ratio <= 1.0:
            return 0.7
        else:
            return 0.4
    
    def _check_signal_clarity(self, audio_data):
        """Check audio signal clarity"""
        if len(audio_data) == 0:
            return 0
        
        # Calculate signal variance
        audio_std = np.std(audio_data)
        audio_mean = np.mean(np.abs(audio_data))
        
        if audio_mean == 0:
            return 0
        
        # Clarity based on signal-to-variance ratio
        clarity = min(1.0, audio_std / (audio_mean * 2))
        return clarity
    
    def _calculate_snr(self, audio_data):
        """Estimate signal-to-noise ratio"""
        if len(audio_data) < 100:
            return 0.5
        
        # Simple SNR estimation using percentiles
        signal_power = np.percentile(np.abs(audio_data), 90)
        noise_power = np.percentile(np.abs(audio_data), 10)
        
        if noise_power == 0:
            return 1.0
        
        snr = signal_power / noise_power
        return min(1.0, snr / 10)  # Cap at 10x SNR
    
    def _get_quality_label(self, score):
        """Get quality description based on score"""
        if score >= 85:
            return "Excellent ⭐⭐⭐"
        elif score >= 70:
            return "Good ⭐⭐"
        elif score >= 50:
            return "Fair ⭐"
        elif score >= 30:
            return "Poor ⚠️"
        else:
            return "Unreliable ❌"
    
    def get_recommendation(self, score):
        """Get suggestions for improvement"""
        if score < 50:
            return "Try speaking louder or reducing background noise"
        elif score < 70:
            return "Speak at a consistent pace with clear pauses"
        elif score < 85:
            return "Good! Practice with different speeds"
        else:
            return "Excellent! You're ready for advanced practice"