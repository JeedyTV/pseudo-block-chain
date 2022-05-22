import json

class Transaction(dict):
    
    def __init__(self,*args):
        """A transaction, in our KV setting. A transaction typically involves
        some key, value and an origin (the one who put it onto the storage).
        Args:
        origin (string): address of the peer who create the transaction
        key (string): key of the transaction
        value (string): value of the transaction
        timestamp (string): Time at which the transaction was created
        """
        #first constructor instantiate from 4 values
        if len(args)==4:
            self.origin = args[0] #adress of the peer
            self.key = args[1]
            self.value = args[2]
            self.timestamp = args[3]
            dict.__init__(self,origin=args[0],key=args[1],value=args[2],timestamp=args[3])
        #second constructor instantiate from a json like string
        elif len(args)==1:
            t = json.loads(args[0])
            self.origin = t['origin'] #adress of the peer
            self.key = t['key']
            self.value = t['value']
            self.timestamp = t['timestamp']
            dict.__init__(self,origin=t['origin'],key=t['key'],value=t['value'],timestamp=t['timestamp'])
    
    def __str__(self) -> str:
        return str(self.__dict__).replace('\'','\"')
    
    def __repr__(self) -> str:
        return str(self.__dict__).replace('\'','\"')
        
    def __eq__(self, __o: object) -> bool:
        
        if self.origin == __o.origin and self.key == __o.key \
            and self.value ==__o.value and self.timestamp == __o.timestamp:
           return True
        else:
            return False