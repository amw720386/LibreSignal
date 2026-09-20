"""
All your implementation code for the bank system simulation goes here.
"""
class InMemoryDatabase:
    def __init__(self):
        self.data = {}
        self.history = []
        self.backups = {}
        self.history_backups = {}
    
    # ========== Level 1 Operations ==========
    def set(self,key, field, value):
        if key not in self.data:
            self.data[key] = {field: value}
        else:
            self.data[key][field] = value


        return ""
    
    def get(self,key, field):
        if key not in self.data:
            return ""
        if field not in self.data[key]:
            return ""
        
        return self.data[key][field]

    def delete(self,key, field):
        if key not in self.data:
            return 'false'
        if field not in self.data[key]:
            return 'false'
        
        del self.data[key][field]

        return 'true'
        
    
    # ========== Level 2 Operations ==========
    def scan(self, key):
        if key not in self.data:
            return ""
        
        out = ""

        for m, n in sorted(self.data[key].items()):
            out += f"{m}({n}), "

        if len(out) > 2:
            out = out[:-2]

        return out

    def scan_by_prefix(self, key, prefix):
        if key not in self.data:
            return ""
        
        out = ""

        for m, n in sorted(self.data[key].items()):
            if m.startswith(prefix):
                out += f"{m}({n}), "

        if len(out) > 2:
            out = out[:-2]

        return out

    # ========== Level 3 Operations ==========
    def set_at(self, key, field, value, timestamp):
        self.update_ttl(timestamp)

        if key not in self.data:
            self.data[key] = {field: value}
        else:
            self.data[key][field] = value

        self.history.append({"command": "set_at", "time": timestamp, "key": key, "field": field, "value": value})

        return ""

    def set_at_with_ttl(self, key, field, value, timestamp, ttl):
        self.update_ttl(timestamp)

        if key not in self.data:
            self.data[key] = {field: value}
        else:
            self.data[key][field] = value

        self.history.append({"command": "set_at_with_ttl", "time": timestamp, "key": key, "field": field, "value": value, "ttl": ttl})

        return ""

    def delete_at(self, key, field, timestamp):
        self.update_ttl(timestamp)

        if key not in self.data:
            return 'false'
        if field not in self.data[key]:
            return 'false'
        
        del self.data[key][field]

        return 'true'

    def get_at(self, key, field, timestamp):
        self.update_ttl(timestamp)

        if key not in self.data:
            return ""
        if field not in self.data[key]:
            return ""
        
        return self.data[key][field]

    def scan_at(self, key, timestamp):
        self.update_ttl(timestamp)

        if key not in self.data:
            return ""
        
        out = ""

        for m, n in sorted(self.data[key].items()):
            out += f"{m}({n}), "

        if len(out) > 2:
            out = out[:-2]

        return out

    def scan_by_prefix_at(self, key, prefix, timestamp):
        self.update_ttl(timestamp)

        if key not in self.data:
            return ""
        
        out = ""

        for m, n in sorted(self.data[key].items()):
            if m.startswith(prefix):
                out += f"{m}({n}), "

        if len(out) > 2:
            out = out[:-2]

        return out

    # ========== Level 4 Operations ==========
    def backup(self, timestamp):
        self.update_ttl(timestamp)
        
        self.backups[timestamp] = {
            key: fields.copy()  
            for key, fields in self.data.items()
        }

        self.history_backups[timestamp] = [
            log.copy() for log in self.history
        ]

        for log in self.history_backups[timestamp]:
            if log["command"] == "set_at_with_ttl":
                log["ttl"] = (log["time"] + log["ttl"]) - timestamp

        out = 0

        for key, value in self.backups[timestamp].items():
            if key and value:
                out += 1

        return str(out)

    def restore(self, timestamp, timestampToRestore):
        chosen_time = 0

        for time in self.backups.keys():
            if time > chosen_time and time <= timestampToRestore:
                chosen_time = time
        
        self.data = self.backups[chosen_time]
        self.history = self.history_backups[chosen_time]
        for log in self.history:
            if log["command"] == "set_at_with_ttl":
                log["time"] = timestamp


        return ""


    def update_ttl(self, timestamp):
        for log in self.history:
            if log["command"] == "set_at_with_ttl":
                if log["time"] + log["ttl"] <= timestamp:
                    if log["key"] in self.data and log["field"] in self.data[log["key"]] and self.data[log["key"]][log["field"]] == log["value"]:
                        self.delete(log["key"], log["field"])
                        log["command"] = "set_at_with_ttl_done"