import socket

def run_at_slac():
    """Decide if we are running locally at SLAC or not
    """
    hostname = socket.getfqdn()
    print("Running on host: ", hostname)
    run_at_slac = False
    if hostname.startswith("sdfmilan") or hostname.endswith("slac.stanford.edu"):
        run_at_slac = True
    return run_at_slac

if __name__=="__main__":
    print(run_at_slac())