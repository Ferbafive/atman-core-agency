class LeadQualifier:
    """
    Clase para calificar leads basándose en criterios específicos.
    """
    
    def __init__(self, criteria=None):
        """
        Inicializa el LeadQualifier con criterios de calificación.
        
        Args:
            criteria (dict): Diccionario con criterios de calificación
        """
        self.criteria = criteria or {
            'min_score': 0,
            'max_score': 100,
            'required_fields': []
        }
    
    def calculate_score(self, lead_data):
        """
        Calcula el score de un lead basándose en los criterios de calificación.
        
        Args:
            lead_data (dict): Datos del lead a evaluar
            
        Returns:
            float: Score del lead
        """
        score = 0
        max_possible_score = 0
        
        # Calcular score basado en los criterios
        for field, weight in self.criteria.get('weights', {}).items():
            if field in lead_data:
                max_possible_score += weight
                score += weight
        
        # Calcular score normalizado
        normalized_score = min(100, (score / max_possible_score * 100) if max_possible_score > 0 else 0)
        
        return normalized_score
    
    def qualify_lead(self, lead_data):
        """
        Evalúa si un lead cumple con los criterios de calificación.
        
        Args:
            lead_data (dict): Datos del lead a evaluar
            
        Returns:
            dict: Resultado de la calificación con score y estado
        """
        score = self.calculate_score(lead_data)
        
        # Determinar estado
        status = self._determine_status(score)
        
        return {
            'lead_id': lead_data.get('id', 'unknown'),
            'score': score,
            'status': status,
            'qualified': status == 'qualified',
            'criteria_met': self._check_criteria_met(lead_data)
        }
    
    def _determine_status(self, score):
        """
        Determina el estado del lead basado en el score.
        
        Args:
            score (float): Score del lead
            
        Returns:
            str: Estado del lead ('qualified', 'warm', 'cold')
        """
        if score >= 70:
            return 'qualified'
        elif score >= 40:
            return 'warm'
        else:
            return 'cold'
    
    def _check_criteria_met(self, lead_data):
        """
        Verifica si el lead cumple con los criterios requeridos.
        
        Args:
            lead_data (dict): Datos del lead
            
        Returns:
            bool: True si cumple, False si no cumple
        """
        required_fields = self.criteria.get('required_fields', [])
        return all(field in lead_data for field in required_fields)
    
    def get_qualification_report(self, leads):
        """
        Genera un reporte de calificación para múltiples leads.
        
        Args:
            leads (list): Lista de leads a calificar
            
        Returns:
            list: Lista de reportes de calificación
        """
        return [self.qualify_lead(lead) for lead in leads]
