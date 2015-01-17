class Line:
    
    def __init__(self, number, charges):
        self.number = number
        self.charges = charges
    
    def update_all(self, surcharges_difference, government_fees_difference):
        self.update_monthly_charges()
        self.update_talk_usage_charges()
        self.update_surcharges(surcharges_difference)
        self.update_government_fees(government_fees_difference)
        
    def update_monthly_charges(self):
        if self.number == '806-786-2712':
            self.charges['Monthly Plan Charges'] = self.charges['Monthly Plan Charges'] - 80 + 80 / 5
        else:
            self.charges['Monthly Plan Charges'] = self.charges['Monthly Plan Charges'] + 80 / 5

    def update_talk_usage_charges(self):
        if not self.charges.has_key('Talk Usage Charges'):
            self.charges.update({'Talk Usage Charges' : 0})
            
    def update_surcharges(self, difference):
        if self.number == '806-786-2712':
            self.charges['Surcharges And Fees'] = self.charges['Surcharges And Fees'] - 4 * difference / 5
        else:
            self.charges['Surcharges And Fees'] = self.charges['Surcharges And Fees'] + difference / 5
        if len(self.charges) > 4:

            for key, value in self.charges.copy().iteritems():
                if key != 'Monthly Plan Charges' and key != 'Surcharges And Fees' and \
                key != 'Government Fees Taxes' and key != 'Talk Usage Charges':
                    self.charges['Surcharges And Fees'] = self.charges['Surcharges And Fees'] + value
                    del self.charges[key]
            
    def update_government_fees(self, difference):
        if self.number == '806-786-2712':
            self.charges['Government Fees Taxes'] = self.charges['Government Fees Taxes'] - 4 * difference / 5
        else:
            self.charges['Government Fees Taxes'] = self.charges['Government Fees Taxes'] + difference / 5
    
    def get_total(self):
        return sum(self.charges.values())