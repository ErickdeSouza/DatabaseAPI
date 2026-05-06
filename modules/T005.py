from concurrent.futures import ThreadPoolExecutor 

class Separate:
***REMOVED***
***REMOVED***pass
***REMOVED***
***REMOVED***@staticmethod
***REMOVED***def iniciate(size, func, args):
***REMOVED***with ThreadPoolExecutor(max_workers=size) as executor:
***REMOVED******REMOVED***executor.map(func, args)