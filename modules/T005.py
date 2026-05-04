from concurrent.futures import ThreadPoolExecutor
import time 

class Separate:
***REMOVED***
***REMOVED***pass
***REMOVED***
***REMOVED***@staticmethod
***REMOVED***def iniciate(size, func, args):
***REMOVED***with ThreadPoolExecutor(max_workers=size) as executor:
***REMOVED******REMOVED***executor.map(func, args)