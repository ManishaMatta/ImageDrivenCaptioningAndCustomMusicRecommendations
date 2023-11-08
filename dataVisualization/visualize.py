from IPython.display import IFrame

class VisualizeModule:
    @staticmethod
    def song():
        documentation = IFrame(src='https://p.scdn.co/mp3-preview/4bd2dc84016f3743add7eea8b988407b1b900672?cid=9d7429fddef847139c8ae837b6bcdd92', width=500, height=50)
        display(documentation)
