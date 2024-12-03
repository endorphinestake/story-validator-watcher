from configparser import RawConfigParser

class Config():
    config_dir = 'configs/'
    
    def __init__(self, config_file_name: str='config.ini'):
        self.config_file_name = config_file_name
        self.set_config()
            
    def set_config(self):
        try:
            self.params = RawConfigParser()
            self.params.read(self.get_config_path())
        except Exception as e:
            print(e)

    def get(self, section: str, param: str, val_type: object = None) -> any:
        try:
            section = section.lower()
            param = param.lower() 
            value = self.params[section][param]
        except Exception as e:
            print(e)
            return None
        
        if val_type == None:
            value = self.parse_value(value)
        else:
            value = val_type(value)
        
        return value
    
    def parse_value(self, value: str) -> any:
        list_val = self.check_for_list(value)
        if list_val != None: return list_val

        value = self.check_single_value(value)
        
        return value
    
    def check_single_value(self, value: str) -> any:
        boolean = self.check_for_boolean(value)
        if boolean != None: return boolean
        
        number = self.check_for_number(value)
        if number != None: return number
        
        return value
    
    def check_for_boolean(self, value: str) -> bool:
        if value.lower() == 'false':
            return False
        if value.lower() == 'true':
            return True
        return None
    
    def check_for_number(self, value: str) -> int:
        try:
            value = float(value)
            return value
        except: 
            return None
        
    def check_for_list(self, value: str) -> list:
        try:
            str_value = value
            if str_value[:1] == '(' and str_value[-1:] == ')':
                str_value = str_value.replace('(', '').replace(')', '')
                str_value = str_value.replace(', ', ',')
                
                value_list = str_value.split(',')
                for index, value in enumerate(value_list):
                    value = self.check_single_value(value)
                    value_list[index] = value
                    
                return value_list
            
            else: raise
        except: return None
    
    def get_config_path(self) -> str:
        return self.config_dir + self.config_file_name

    def change_param(self, section: str, param: str, value: any):
        self.params.set(section, param, value)        
        self.update_file()
    
    def update_file(self):    
        with open(self.get_config_path(), 'w') as configfile:
            self.params.write(configfile)
