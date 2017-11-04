import json

class VideoEventModel():
    def __init__(self,id, start, stop, posX, posY, resType, resPath):
        self.id = id
        self.start=start
        self.stop=stop
        self.posX=posX
        self.posY=posY
        self.resType=resType
        self.resPath=resPath

    def get_description(self):
        return self.__str__()

    def toDict(self):
        return dict(id=self.id, start=self.start, stop=self.stop, posX=self.posX, posy=self.posY, resource=self.resType, path=self.resPath);

    def __repr__(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return str(self.toDict())

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)