#Linear metadata model for testing purposes
from comet_ml import Experiment
import tensorflow as tf
from DeepTreeAttention.trees import AttentionModel
from DeepTreeAttention.models import metadata
from DeepTreeAttention.callbacks import callbacks
import pandas as pd

model = AttentionModel(config="/home/b.weinstein/DeepTreeAttention/conf/tree_config.yml")
model.create()

#Log config
experiment = Experiment(project_name="neontrees", workspace="bw4sz")
experiment.log_parameters(model.config["train"])
experiment.log_parameters(model.config["evaluation"])    
experiment.log_parameters(model.config["predict"])
experiment.add_tag("RGB")

##Train

#Train see config.yml for tfrecords path with weighted classes in cross entropy
model.read_data("RGB_train")
class_weight = model.calc_class_weight()

##Train subnetwork
experiment.log_parameter("Train subnetworks", True)
with experiment.context_manager("RGB_spatial_subnetwork"):
    print("Train RGB spatial subnetwork")
    model.read_data(mode="RGB_submodel")
    model.train(submodel="spatial", sensor="rgb",class_weight=[class_weight, class_weight, class_weight], experiment=experiment)

with experiment.context_manager("RGB_spectral_subnetwork"):
    print("Train RGB spectral subnetwork")    
    model.read_data(mode="RGB_submodel")   
    model.train(submodel="spectral", sensor="rgb", class_weight=[class_weight, class_weight, class_weight], experiment=experiment)
        
#Train full model
with experiment.context_manager("RGB_model"):
    experiment.log_parameter("Class Weighted", True)
    model.read_data(mode="RGB_train")
    model.train(class_weight=class_weight, sensor="rgb", experiment=experiment)
    
    #Get Alpha score for the weighted spectral/spatial average. Higher alpha favors spatial network.
    if model.config["train"]["RGB"]["weighted_sum"]:
        estimate_a = model.RGB_model.get_layer("weighted_sum").get_weights()
        experiment.log_metric(name="spatial-spectral weight", value=estimate_a[0][0])