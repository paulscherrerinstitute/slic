import rich.progress as rp


class Progress(rp.Progress):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("expand", True)
        super().__init__(*args, **kwargs)

    @classmethod
    def get_default_columns(cls):
        return (
            rp.TextColumn("[progress.description]{task.description}"),
            rp.BarColumn(bar_width=None), # use available space
            rp.TaskProgressColumn(),
            rp.TimeRemainingColumn(),
            SpeedColumn()
        )


class SpeedColumn(rp.ProgressColumn):

    def render(self, task):
        speed = task.finished_speed or task.speed
        return rp.TaskProgressColumn.render_speed(speed)





if __name__ == "__main__":
    from time import sleep

    n = 10
    with Progress() as progress:
        task = progress.add_task("test", total=n)
        for _ in range(n):
            sleep(1/n)
            progress.update(task, advance=1)
        progress.close_task(task)



