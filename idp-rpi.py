from multiprocessing import Process, Pipe
import sys

import core.bootstrap as bootstrap
import core.controller as controller
import monitoring.monitoring as monitoring

if __name__ == "__main__":
    try:
        controller_conn, monitoring_conn = Pipe()
        mon_p = Process(target=monitoring.start, args=(monitoring_conn, ))
        mon_p.start()

        interface = bootstrap.bootstrap_interface()
        interface_conn, controller_conn2 = Pipe()

        con_p = Process(target=controller.start, args=(controller_conn, controller_conn2))
        con_p.start()

        interface.start(bootstrap.bootstrap_assignments(), interface_conn)

        con_p.join()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(1)
