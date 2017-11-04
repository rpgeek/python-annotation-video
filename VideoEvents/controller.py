import model

class VideoEventsController():

    def __init__(self):
        self.events_dict = dict()

    def addModel(self,id, start, stop, posX, posY, resType, resPath ):
        self.events_dict[id]= model.VideoEventModel(id, start, stop, posX, posY, resType, resPath);

    def addModel(self, eventObj ):
        self.events_dict[eventObj.id]= eventObj;
        strdict = str(eventObj)
        print('adding model to controller ',strdict )

    def removeModel(self, id):
        del self.events_dict[id];