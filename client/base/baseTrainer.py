from abc import abstractmethod
from ...util import jsonFormat 
from ...chainfl.interact import chainProxy

class BaseTrainer:
    """
    Base class for all trainers.
    Each client trainer need to complement the method below.
    """
    def __init__(self, model, criterion, optimizer, config):
        '''
        :param
        model: pass the init model to this trainer
        criterion: the loss function
        config: dict prepare to provide some flexible choice in the future
        
        '''
        self.config = config
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.pipe = chainProxy()
        
        self.id = config["client_id"]
        # cfg_trainer = config['trainer']
        # self.epochs = cfg_trainer['epochs']
        self.start_epoch = 1 # 0 or 1 
        
    @abstractmethod
    def _train_epoch(self, epoch, dataloader):
        """
        :info: Training logic for an epoch including the forward and the backward propagation
        
        :param epoch: Current epoch number
        
        :return format : using a dict to return 
            return some result in this epoch like loss ,accuarcy and other  
            example:
                  return result = {
                      'loss' : 1.2222
                      'accuarcy' : 0.99
                      ... 
                  }
        """
        raise NotImplementedError

    def train(self):
        """
        Full training logic
        """
        for epoch in range(self.start_epoch, self.epochs + 1):
            result = self._train_epoch(epoch)
            response = self._upload_model(epoch)
            self.model = self._download_model(epoch)
    @abstractmethod
    def _on_before_upload(self,epoch):
        '''
        Here may do some thing before upload like compression, crypto
        '''
        raise NotImplementedError
    
    @abstractmethod
    def _on_after_download(self,epoch):
        '''
        Here may do some thing after download, the download model may be a compressed one or cryptoed one.
        '''
        
        raise NotImplementedError
    
    @abstractmethod
    def _upload_model(self, epoch):
        """
        Upload the current trained method to blockchain
        use a json string to pass the infomation the blockchain needed.
        :example: uploaded_para = {
                      'epoch' : 3
                      'model' : json-like(model.state_dict() using util.JsonFormat to convert the dict into json) 
                      'client_id' : self.id
                      ... 
                  }
        """
        uploaded_para = {
            'epoch': epoch,
            'state_dict': self.model.state_dict(),
            'client_id': self.id
        }
        self.pipe.upload_model(uploaded_para)
        
    
    @abstractmethod
    def _download_model(self,epoch):
        """
        Resume from saved checkpoints
        :param resume_path: Checkpoint path to be resumed
        """
        self.pipe.download_model()
        
        
# if __name__ == '__main__':
#     #No test needed for an abstract method