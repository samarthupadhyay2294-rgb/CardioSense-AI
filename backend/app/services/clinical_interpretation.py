"""
Clinical Interpretation Service for ECG Analysis

This service provides structured research/educational interpretation of ECG predictions
by combining ML predictions with extracted signal features. It does NOT replace
the ML model but provides context and explanation for the prediction.

IMPORTANT: This interpretation is for research and educational purposes only.
It is NOT a clinical diagnosis and should NOT be used for medical decision-making.
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ClinicalInterpreter:
    """
    Generate clinically relevant interpretations from ECG predictions and features.
    
    This service interprets ML predictions in the context of extracted signal features
    to provide structured, research/educational interpretation. It follows rule-based
    logic to explain findings and provide context.
    
    NOTE: This is NOT a clinical diagnosis. All interpretations must be confirmed
    by qualified healthcare professionals.
    """
    
    def __init__(self):
        # Clinical rules for each prediction class
        self.clinical_rules = {
            "NORM": {
                "criteria": ["normal_sinus_rhythm"],
                "urgency": "none",
                "description": "Normal sinus rhythm",
                "clinical_context": "No significant abnormalities detected in the ECG signal."
            },
            "MI": {
                "criteria": ["ST_elevation", "pathological_Q", "T_wave_inversion"],
                "urgency": "emergency",
                "description": "Signs of myocardial infarction",
                "clinical_context": "ECG patterns suggestive of myocardial injury or infarction."
            },
            "STTC": {
                "criteria": ["ST_depression", "T_wave_flattening", "ST_elevation"],
                "urgency": "urgent",
                "description": "ST/T wave changes",
                "clinical_context": "Abnormalities in ST segments and T waves indicating possible ischemia."
            },
            "CD": {
                "criteria": ["QRS_widening", "bundle_branch_block"],
                "urgency": "routine",
                "description": "Conduction disturbance",
                "clinical_context": "Abnormalities in electrical conduction through the heart."
            },
            "HYP": {
                "criteria": ["high_voltage", "strain_pattern"],
                "urgency": "routine",
                "description": "Ventricular hypertrophy",
                "clinical_context": "Evidence of increased ventricular muscle mass."
            }
        }
        
        # Feature thresholds for interpretation
        self.thresholds = {
            "heart_rate_tachycardia": 100.0,
            "heart_rate_bradycardia": 60.0,
            "hrv_reduced": 10.0,
            "st_elevation_significant": 0.1,
            "st_depression_significant": 0.1,
            "qrs_widening": 0.12,
            "qt_prolonged": 0.44
        }
    
    def interpret_prediction(
        self, 
        prediction: Dict, 
        features: Optional[Dict] = None,
        signal_quality: Optional[str] = None
    ) -> Dict:
        """
        Generate clinical interpretation from prediction and features.
        
        Args:
            prediction: ML prediction result with prediction_code, confidence, etc.
            features: Extracted ECG features (temporal, frequency, morphological)
            signal_quality: Signal quality assessment
            
        Returns:
            Structured interpretation with findings, significance, recommendations, etc.
        """
        prediction_code = prediction.get("prediction_code", "NORM")
        confidence = prediction.get("confidence", 0.0)
        prediction_label = prediction.get("prediction", prediction_code)
        
        # Initialize interpretation structure
        interpretation = {
            "primary_findings": [],
            "secondary_findings": [],
            "clinical_significance": "",
            "urgency": "none",
            "recommendations": [],
            "differential_diagnosis": [],
            "limitations": [],
            "feature_analysis": {},
            "prediction_context": {}
        }
        
        # Add prediction context
        interpretation["prediction_context"] = {
            "prediction": prediction_label,
            "prediction_code": prediction_code,
            "confidence": confidence,
            "confidence_level": self._assess_confidence(confidence)
        }
        
        # Signal quality consideration
        if signal_quality:
            interpretation["signal_quality"] = signal_quality
            if signal_quality == "poor":
                interpretation["limitations"].append(
                    "Signal quality is poor - interpretation may be unreliable"
                )
        
        # Primary interpretation based on prediction
        if prediction_code in self.clinical_rules:
            rule = self.clinical_rules[prediction_code]
            interpretation["primary_findings"].append(rule["description"])
            interpretation["urgency"] = rule["urgency"]
            interpretation["clinical_significance"] = rule["clinical_context"]
        
        # Analyze features for additional findings
        if features:
            interpretation["feature_analysis"] = self._analyze_features(features)
            interpretation["secondary_findings"].extend(
                interpretation["feature_analysis"]["additional_findings"]
            )
        
        # Generate clinical significance based on findings
        interpretation["clinical_significance"] = self._generate_clinical_significance(
            prediction_code, confidence, interpretation
        )
        
        # Generate recommendations
        interpretation["recommendations"] = self._generate_recommendations(
            prediction_code, interpretation["urgency"]
        )
        
        # Generate differential diagnosis
        interpretation["differential_diagnosis"] = self._generate_differential_diagnosis(
            prediction_code, features
        )
        
        # Add standard limitations
        interpretation["limitations"].extend(self._get_standard_limitations())
        
        logger.info(f"Generated interpretation for {prediction_code} (confidence: {confidence:.3f})")
        
        return interpretation
    
    def _analyze_features(self, features: Dict) -> Dict:
        """Analyze extracted features for clinical findings."""
        additional_findings = []
        feature_summary = {}
        
        # Analyze temporal features
        temporal_features = features.get("temporal", {})
        
        # Heart rate analysis
        heart_rate_anomalies = []
        for lead_name, lead_features in temporal_features.items():
            hr = lead_features.get("heart_rate", {})
            mean_hr = hr.get("mean", 0)
            
            if mean_hr > self.thresholds["heart_rate_tachycardia"]:
                heart_rate_anomalies.append(f"Tachycardia in {lead_name} ({mean_hr:.0f} BPM)")
            elif mean_hr > 0 and mean_hr < self.thresholds["heart_rate_bradycardia"]:
                heart_rate_anomalies.append(f"Bradycardia in {lead_name} ({mean_hr:.0f} BPM)")
            
            # HRV analysis
            hr_std = hr.get("std", 0)
            if hr_std > self.thresholds["hrv_reduced"]:
                additional_findings.append(f"Reduced heart rate variability in {lead_name}")
        
        if heart_rate_anomalies:
            additional_findings.extend(heart_rate_anomalies)
            feature_summary["heart_rate"] = heart_rate_anomalies
        
        # ST segment analysis
        st_findings = []
        for lead_name, lead_features in temporal_features.items():
            st_segment = lead_features.get("st_segment", {})
            st_elevation = st_segment.get("elevation", 0)
            st_depression = st_segment.get("depression", 0)
            
            if st_elevation > self.thresholds["st_elevation_significant"]:
                st_findings.append(
                    f"ST elevation in lead {lead_name} ({st_elevation:.2f} mV)"
                )
            if st_depression > self.thresholds["st_depression_significant"]:
                st_findings.append(
                    f"ST depression in lead {lead_name} ({st_depression:.2f} mV)"
                )
        
        if st_findings:
            additional_findings.extend(st_findings)
            feature_summary["st_segment"] = st_findings
        
        # QRS analysis
        qrs_findings = []
        for lead_name, lead_features in temporal_features.items():
            qrs = lead_features.get("qrs_features", {})
            qrs_duration = qrs.get("duration", 0)
            
            if qrs_duration > self.thresholds["qrs_widening"]:
                qrs_findings.append(
                    f"QRS widening in lead {lead_name} ({qrs_duration:.3f} s)"
                )
        
        if qrs_findings:
            additional_findings.extend(qrs_findings)
            feature_summary["qrs"] = qrs_findings
        
        # QT interval analysis
        qt_findings = []
        for lead_name, lead_features in temporal_features.items():
            qt_interval = lead_features.get("qt_interval", 0)
            
            if qt_interval > self.thresholds["qt_prolonged"]:
                qt_findings.append(
                    f"Prolonged QT interval in lead {lead_name} ({qt_interval:.3f} s)"
                )
        
        if qt_findings:
            additional_findings.extend(qt_findings)
            feature_summary["qt_interval"] = qt_findings
        
        return {
            "additional_findings": additional_findings,
            "summary": feature_summary
        }
    
    def _assess_confidence(self, confidence: float) -> str:
        """Assess confidence level."""
        if confidence >= 0.9:
            return "high"
        elif confidence >= 0.7:
            return "moderate"
        elif confidence >= 0.5:
            return "low"
        else:
            return "very_low"
    
    def _generate_clinical_significance(
        self, 
        prediction_code: str, 
        confidence: float, 
        interpretation: Dict
    ) -> str:
        """Generate clinical significance statement."""
        if prediction_code == "NORM":
            if confidence > 0.8:
                return "Normal ECG with high confidence. No significant abnormalities detected."
            else:
                return "Likely normal ECG, though confidence is moderate. No significant abnormalities detected."
        
        urgency = interpretation.get("urgency", "none")
        findings = " and ".join(interpretation["primary_findings"])
        confidence_level = interpretation["prediction_context"]["confidence_level"]
        
        confidence_note = ""
        if confidence_level == "low" or confidence_level == "very_low":
            confidence_note = " (low confidence - requires confirmation)"
        
        if urgency == "emergency":
            return f"EMERGENCY: {findings}{confidence_note}. Immediate medical evaluation required."
        elif urgency == "urgent":
            return f"URGENT: {findings}{confidence_note}. Prompt medical evaluation recommended."
        else:
            return f"{findings}{confidence_note}. Clinical correlation recommended."
    
    def _generate_recommendations(self, prediction_code: str, urgency: str) -> List[str]:
        """Generate clinical recommendations."""
        recommendations = []
        
        # Base recommendations by urgency
        if urgency == "emergency":
            recommendations.extend([
                "Seek immediate emergency medical care",
                "Do not delay evaluation for any reason",
                "Consider activating emergency response system if symptoms are severe"
            ])
        elif urgency == "urgent":
            recommendations.extend([
                "Seek prompt medical evaluation",
                "Contact healthcare provider within 24 hours",
                "Monitor for worsening symptoms"
            ])
        else:
            recommendations.extend([
                "Schedule routine follow-up with healthcare provider",
                "Continue regular cardiac monitoring if indicated",
                "Discuss findings with primary care physician"
            ])
        
        # Specific recommendations based on prediction
        if prediction_code == "MI":
            recommendations.append("Consider cardiac enzyme evaluation (troponin)")
            recommendations.append("Consider urgent cardiology consultation")
        elif prediction_code == "STTC":
            recommendations.append("Consider stress testing or cardiac imaging")
            recommendations.append("Evaluate for coronary artery disease")
        elif prediction_code == "CD":
            recommendations.append("Consider cardiology consultation for conduction evaluation")
            recommendations.append("Consider Holter monitoring if symptomatic")
        elif prediction_code == "HYP":
            recommendations.append("Consider echocardiography for structural evaluation")
            recommendations.append("Evaluate for hypertension management")
        
        return recommendations
    
    def _generate_differential_diagnosis(
        self, 
        prediction_code: str, 
        features: Optional[Dict] = None
    ) -> List[str]:
        """Generate differential diagnosis suggestions."""
        differential = []
        
        if prediction_code == "MI":
            differential.extend([
                "Acute myocardial infarction",
                "Previous myocardial infarction with scar",
                "Left ventricular aneurysm",
                "Pericarditis",
                "Early repolarization pattern"
            ])
        elif prediction_code == "STTC":
            differential.extend([
                "Myocardial ischemia",
                "Electrolyte abnormalities (e.g., hypokalemia)",
                "Drug effects (e.g., digoxin, beta-blockers)",
                "Normal variant",
                "Myocarditis"
            ])
        elif prediction_code == "CD":
            differential.extend([
                "Bundle branch block (left or right)",
                "Hemiblock",
                "Intraventricular conduction delay",
                "Ventricular preexcitation (WPW)",
                "Non-specific intraventricular conduction delay"
            ])
        elif prediction_code == "HYP":
            differential.extend([
                "Left ventricular hypertrophy",
                "Right ventricular hypertrophy",
                "Athlete's heart",
                "Volume overload",
                "Early repolarization"
            ])
        
        return differential
    
    def _get_standard_limitations(self) -> List[str]:
        """Get standard limitations and disclaimers."""
        return [
            "AI interpretation should be confirmed by qualified healthcare professional",
            "Clinical correlation with patient symptoms and history is required",
            "Model trained on specific dataset, may not generalize to all populations",
            "This is for research and educational purposes only, not clinical diagnosis",
            "Signal features are estimated, not clinically validated measurements",
            "Interpretation does not replace comprehensive clinical evaluation"
        ]


# Global instance
clinical_interpreter = ClinicalInterpreter()
