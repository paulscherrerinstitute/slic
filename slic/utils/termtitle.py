
def termtitle(title):
    title = "\33]0;" + str(title) + "\a"
    print(title, end="", flush=True)


