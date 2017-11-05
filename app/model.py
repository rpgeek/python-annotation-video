import json


class VideoEventModel():
    def __init__(self, id, start, stop, posX, posY, resType, resPath):
        self.id = id
        self.start = start
        self.stop = stop
        self.posX = posX
        self.posY = posY
        self.resType = resType
        self.resPath = resPath

    @property
    def get_description(self):
        return self.__str__()

    @property
    def to_dict(self):
        return dict(id=self.id, start=self.start,
                    stop=self.stop, posX=self.posX,
                    posy=self.posY, resource=self.resType,
                    path=self.resPath)

    def __repr__(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return str(self.to_dict)

    def to_json(self):
        return json.dumps(self,
                          default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
