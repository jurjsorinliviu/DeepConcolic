
from datetime import datetime
import os

import keras
from keras.models import *
from keras.datasets import cifar10
from keras.datasets import mnist
from keras.applications.vgg16 import VGG16
from keras.preprocessing.image import load_img
from keras.layers import *
from keras import *
from utils import *
from nc_lp import *
from lp_encoding import *


def nc_setup(test_object, outs):
  print('\n== {0}, {1} ==\n'.format(test_object.criterion, test_object.norm))
  if not os.path.exists(outs):
    os.system('mkdir -p {0}'.format(outs))
  if not outs.endswith('/'):
    outs+='/'
  nc_results=outs+'nc_{0}_report-{1}.txt'.format(test_object.norm, str(datetime.now()).replace(' ', '-'))
  nc_results=nc_results.replace(':', '-')

  layer_functions=get_layer_functions(test_object.dnn)
  print('\n== Got layer functions: {0} ==\n'.format(len(layer_functions)))
  cover_layers=get_cover_layers(test_object.dnn, 'NC')
  print('\n== Got cover layers: {0} ==\n'.format(len(cover_layers)))

  tot_size=10000
  if len(test_object.raw_data.data)<tot_size: tot_size=len(test_object.raw_data.data)
  activations=[]
  batches=np.array_split(test_object.raw_data.data[0:tot_size], tot_size/1000 + 1)
  for batch in batches:
    activations.extend(eval_batch(layer_functions, batch))

  calculate_pfactors(activations, cover_layers)

  #### configuration phase done

  test_cases=[]
  adversarials=[]

  xdata=test_object.raw_data.data
  iseed=np.random.randint(0, len(xdata))
  im=xdata[iseed]

  test_cases.append(im)
  update_nc_map_via_inst(cover_layers, eval(layer_functions, im))
  covered, not_covered=nc_report(cover_layers)
  #print (covered)
  print('\n== neuron coverage: {0}==\n'.format(covered*1.0/(covered+not_covered)))
  #print (np.argmax(test_object.dnn.predict(np.array([im]))))
  #return
  #y = test_object.dnn.predict_classes(np.array([im]))[0]
  #y=(np.argmax(test_object.dnn.predict(np.array([im]))))
  save_an_image(im, 'seed-image', outs)
  #return
  f = open(nc_results, "a")
  f.write('NC-cover: {0} #test cases: {1} #adversarial examples: {2}\n'.format(1.0 * covered / (covered + not_covered), len(test_cases), len(adversarials)))
  f.close()

  for i in range(0, len(cover_layers)):
    cover_layers[i].initialize_ssc_map()

  return nc_results, layer_functions, cover_layers, activations, test_cases, adversarials
