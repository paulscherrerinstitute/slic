try:
    import rich
except ImportError:
    from .pbartqdm import pbar
else:
    from .pbarrich import pbar





if __name__ == "__main__":
    from time import sleep

    def scan(nscan, nacq, nmov):
        for _ in pbar(range(nscan), "[yellow]Scanning..."):
            acquire(nacq)
            move(nmov)

    def acquire(ntotal):
        for _ in pbar(range(ntotal), "[green]Acquiring..."):
            sleep(0.01) # simulate work

    def move(ntotal):
        for _ in pbar(range(ntotal), "[blue]Moving..."):
            sleep(0.00001) # simulate work


    def test1D():
        with pbar(description="test", total=10) as pb:
            for i in range(10):
                sleep(0.1)
                pb.advance()

    def test2D():
        with pbar(description="[green]test1", total=10) as pb1, pbar(description="[blue]test2", total=20) as pb2:
            for i1 in range(10):
                pb2.reset()
                for i2 in range(20):
                    sleep(0.1)
                    pb2.advance()
                pb1.advance()

    def test2Dnested():
        with pbar(description="[green]test1", total=10) as pb1:
            for i1 in range(10):
                with pbar(description="[blue]test2", total=20) as pb2:
                    for i2 in range(20):
                        sleep(0.1)
                        pb2.advance()
                pb1.advance()



    acquire(50)
    move(30000)
    print()

    scan(5, 25, 15000)
    scan(5, 25, 15000)
    print()

    test1D()
    test2D()
    test2Dnested()



