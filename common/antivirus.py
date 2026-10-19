import sys
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="clamd")
import clamd

class AntivirusResult:
    def __init__(self, status: str, details: str | None):
        self._status = status
        self._details = details

    @property
    def is_ok(self) -> bool:
        return self._status == "OK"

    @property
    def details(self) -> str | None:
        return self._details


class Antivirus:

    @staticmethod
    def scan(file_path: str) -> AntivirusResult:
        try:
            clam = clamd.ClamdNetworkSocket(host="localhost", port=3310)
            clam.reload()

            with open(file_path, "rb") as f:
                scan_result = clam.instream(f)

            # Parse the result dictionary, e.g., {'stream': ('OK', None)} or ('FOUND', 'Virus_Name')
            status, details = scan_result.get('stream', ('ERROR', 'Unknown error'))
            return AntivirusResult(status, details)

        except Exception as e:
            return AntivirusResult("ERROR", str(e))

def main():

    if len(sys.argv) == 1:
        file_to_scan = "./eicar.txt"
    else:
        file_to_scan = sys.argv[1]

    print(f"Scanning '{file_to_scan}'...")

    result: AntivirusResult = Antivirus.scan(file_to_scan)

    if result.is_ok:
        print("[+] File is clean.")
    else:
        print(f"[!] File is NOT clean!")
        print(f"Details: {result.details}")


if __name__ == "__main__":
    main()