from multiprocessing import Process, Pipe

import core.bootstrap as bootstrap
import core.controller as controller

if __name__ == "__main__":
    interface = bootstrap.bootstrap_interface()
    parent_conn, child_conn = Pipe()
    con_p = Process(target=controller.start, args=(child_conn,))
    con_p.start()
    interface.start(bootstrap.bootstrap_assignments(), parent_conn)
    con_p.join()