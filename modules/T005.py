from concurrent.futures import ThreadPoolExecutor 

class Separate:
    @staticmethod
    def iniciate(size, func, args):
        with ThreadPoolExecutor(max_workers=size) as executor:
            executor.map(func, args)