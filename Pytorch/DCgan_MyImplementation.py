# -*- coding: utf-8 -*-
"""trainingfield5.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pf6nI3duI8U_k9GnopBMvewbSeatp3-I
"""

ახალი სტატიაა გუგლის, ცოტა ოდენობის სურათებით როგორ გავწვრთნათ მოდელი !!! წაიკითხე და ამ ქვევით მოყვანილზე გამოიყენე!!!
https://ai.googleblog.com/2021/12/training-machine-learning-models-more.html 
https://nn.labml.ai/distillation/index.html

# Commented out IPython magic to ensure Python compatibility.
import os                                # os.path.join(), os.listdir(), os.makedirs() is different from os.mkdir() because first can create nested dirs as well
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# %matplotlib inline
import random
import cv2
import shutil
from IPython.display import Image        # to use sometimes in place of plt.imshow()
# import tarfile
# import PIL.
# from tqdm.notebook import tqdm
# import opendatasets as O

import torch 
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset        # TensorDataset, random_split  ==> 'Dataset' enables custom Datasets(imagefolder/tensordataset), dataloaders and transforms
import torchvision
from torchvision.datasets import ImageFolder            # ImageFolder + datasets like mnist, cifar10 ... get imported from here
#from torchvision.datasets.utils import download_url    # or for google+kaggle datasets ==> !pip install opendatasets --upgrade --quiet ==> import opendatasets as op ==> op.download(url)
from torchvision.utils import make_grid, save_image
import torchvision.transforms as T             # Compose([]), ToTensor(), Normalize(), and for data augmentation -> CenterCrop(), Resize(), RandomCrop(), RandomResizedCrop(), RandomHorizontalFlip(), RandomRotate(), ColorJitter()

manualSeed = 999                       # Set random seed for reproducibility #manualSeed = random.randint(1, 10000) # use if you want new results                                   
print("Random Seed: ", manualSeed)
random.seed(manualSeed)
torch.manual_seed(manualSeed)

#shutil.rmtree('./dirname')             # to delete non empthy directories #ზიპ ფაილებს პირდაპირ ზედ დაკლიკებითშლი ერთი ფაილი რახანაა

def device():
  if torch.cuda.is_available():
    return torch.device('cuda')
  else:
    return torch.device('cpu')
    
device = device()

def todevice(data_model, device):
  if isinstance(data_model, (list, tuple)):
    return [todevice(i, device) for i in data_model]
  return data_model.to(device, non_blocking=True)

class DeviceDataLoader():
  def __init__(self, dataloader, device):
    self.dataloader = dataloader
    self.device = device

  def __iter__(self):
    for batch in self.dataloader:
      yield todevice(batch, self.device)

  def __len__(self):
    return len(self.dataloader)

# !pip install opendatasets --upgrade --quiet                    # downloading with openatasets
# url = 'https://www.kaggle.com/ipythonx/van-gogh-paintings'     
# O.download(url)  

# from zipfile import ZipFile                                    # loading from zip 
# file_name = './archive.zip'
# with ZipFile(file_name, 'r') as zip:
#   zip.extractall()
#   print('Done, now refresh the Files')

! pip install -q kaggle                                         # directdownload from kaggle but first upload Apikey in files
! mkdir ~/.kaggle                                               # https://www.analyticsvidhya.com/blog/2021/06/how-to-load-kaggle-datasets-directly-into-google-colab/ , https://www.kaggle.com/general/74235 
! cp kaggle.json ~/.kaggle/
! chmod 600 ~/.kaggle/kaggle.json
# ! kaggle competitions download <name-of-competition>
! kaggle datasets download splcher/animefacedataset
! unzip animefacedataset

dir = './img'          # this contains another folder 'images' so ./img/images, but we want to have one(more) unnested folder(s) wrapping all images for ImageFolder()
imagesize = 64
batchsize = 128

dataset =      ImageFolder(root=dir,
                           transform=T.Compose([
                               T.Resize(imagesize),
                               T.CenterCrop(imagesize),
                               T.ToTensor(),
                               T.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
                           ]))       
#transform = augmented_normalized_tensorized 
#when pictures have different sizes we want them to be same size
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!! RGB_mean_std_minusonetoonerange = ((0.5, 0.5, 0,5), (0.5, 0.5, 0,5)) ეს Normalize-ს გარეთ არასდროს განსაზღვრო
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!! შველის მარტო terminate session, ისე არ რეფრეშდება შეცდომა!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# def load_image( infilename ) :                                    # imagemanipulations https://www.pluralsight.com/guides/importing-image-data-into-numpy-arrays
#     img = PIL.Image.open( infilename )
#     img.load()
#     data = np.asarray( img, dtype="float64" )
#     return data

# def save_image( npdata, outfilename ) :
#     img = PIL.Image.fromarray( np.asarray( np.clip(npdata,0,255), dtype="uint8"), "L" )
#     img.save( outfilename )

# modifieddata = [load_image(i) for i in os.listdir(dir+'/images') if '.jpg' in i]

#                                                                     #instead Image, plt.imread or cv2.imread
# class CustomImageFolder(Dataset):                                   #https://towardsdatascience.com/beginners-guide-to-loading-image-data-with-pytorch-289c60b7afec, https://stackoverflow.com/questions/62559389/why-am-i-getting-a-divide-by-zero-error-here, https://pytorch.org/tutorials/beginner/data_loading_tutorial.html 
#   def __init__(self, modifieddata, transform):
#     self.data = modifieddata
#     self.transform = transform

#   def __len__(self):
#     return len(self.modifieddata)

#   def __getitem__(self, index):
#     image = self.data[index]
#     transformedimage = self.transform(image)
#     return transformedimage

# traindataset = CustomImageFolder(modifieddata, augmented_normalized_tensorized)

trainloader = torch.utils.data.DataLoader(dataset, batch_size=batchsize, shuffle=True, num_workers=2, pin_memory=True)
trainload = DeviceDataLoader(trainloader, device)

#we do not have validation and test processes like in other casses, but substitute is tracking of change of same images

print(f" There are {len(os.listdir(dir + '/images'))} anime face pictures in {dir}/images folder")
print(f"First 10 images are {os.listdir(dir + '/images')[:10]}")
image, _ = dataset[0]
print(f"image shape is {image.shape}")

def gridofimages(dataload):                        # without for+break images = next(iter(dataload))
  for images, _ in dataload:
    plt.figure(figsize=(8, 8))
    plt.imshow(make_grid(images[:64].cpu().detach(), normalize=True, nrow=8).permute(1, 2, 0))   #images.cpu() because we used dataload (which is on gpu, if gpu is available) not dataloader
    plt.axis('off')
    break
                                                   # normalize=True reverses/unnormalizes what transforms.Normalize has done
gridofimages(trainload)

class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        self.discriminator =  nn.Sequential(
            nn.Conv2d(3, 64, kernel_size = 4, stride = 2, padding = 1, bias=False),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Conv2d(64, 128, kernel_size = 4, stride = 2, padding = 1, bias=False),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Conv2d(128, 256, kernel_size = 4, stride = 2, padding = 1, bias=False),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Conv2d(256, 512, kernel_size = 4, stride = 2, padding = 1, bias=False),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Conv2d(512, 1, kernel_size = 4, stride = 1, padding = 0, bias=False),

            nn.Sigmoid()           # because 0-1 range
        )

    def forward(self, input):
        return self.discriminator(input)


latentsize = 128
class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        self.generator = nn.Sequential(
            nn.ConvTranspose2d(latentsize, 512, kernel_size=4, stride=1, padding=0, bias=False),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),

            nn.ConvTranspose2d(512, 256, kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),

            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),

            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),

            nn.ConvTranspose2d(64, 3, kernel_size=4, stride=2, padding=1, bias=False),

            nn.Tanh() 
        )
    
    def forward(self, input):
        return self.generator(input)


Discriminator = todevice(Discriminator(), device)
Generator = todevice(Generator(), device)


def custom_weights(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find('BatchNorm') != -1:
        nn.init.normal_(m.weight.data, 1.0, 0.02)
        nn.init.constant_(m.bias.data, 0)

Discriminator.apply(custom_weights)
Generator.apply(custom_weights)

def DiscriminatorTraining(images, d_optimizer):
  d_optimizer.zero_grad()

  real_batch_results = Discriminator(images[0]).view(-1)
  real_targets = torch.ones(real_batch_results.size(0), dtype=torch.float, device=device) # torch ones should be given 2 dimensions otherwise if only one parameter, it makes square matrix. + simple way to bring real_targets to GPU device=device
  real_losses = F.binary_cross_entropy(real_batch_results, real_targets)
  real_score = torch.mean(real_batch_results).item()

  latentinput = torch.randn(batchsize, latentsize, 1, 1, device=device)
  fake_images = Generator(latentinput)

  fake_batch_results = Discriminator(fake_images).view(-1)
  fake_targets = torch.zeros(fake_batch_results.size(0), dtype=torch.float, device=device)      #fake_batch_results.size(0) is batchsize
  fake_losses = F.binary_cross_entropy(fake_batch_results, fake_targets)
  fake_score = torch.mean(fake_batch_results).item()
 
  losses = real_losses + fake_losses
  losses.backward()
  d_optimizer.step()

  return losses.item(), real_score, fake_score

def GeneratorTraining(g_optimizer):
  g_optimizer.zero_grad()

  latentinput = torch.randn(batchsize, latentsize, 1, 1, device=device)
  fake_images = Generator(latentinput)

  fake_batch_results = Discriminator(fake_images).view(-1)
  fake_targets = torch.ones(fake_batch_results.size(0), dtype=torch.float, device=device)
  fake_losses = F.binary_cross_entropy(fake_batch_results, fake_targets)
  
  fake_losses.backward()
  g_optimizer.step()

  return fake_losses.item()

#------------------------------------------
quasivalidation_directory = 'gridimages'
os.makedirs(quasivalidation_directory, exist_ok=True)   #exist_ok=True means that it will overwrite if dir already exists

def QuasiValidationSave(index, latentinput, show_gridimage=True):
  fake_images = Generator(latentinput)
  gridimage_name = 'gridimage-number-{0:0=3d}.png'.format(index)
  save_image(fake_images, os.path.join(quasivalidation_directory, gridimage_name), nrow=8)
  if show_gridimage:
    Image(quasivalidation_directory + '/' + gridimage_name)

fixed_first_latentinput = torch.randn(64, latentsize, 1, 1, device=device)
QuasiValidationSave(0, fixed_first_latentinput)
#------------------------------------------

def fit(trainload, lr, epochs):
  torch.cuda.empty_cache()

  D_losses = []
  D_real_scores = []
  D_fake_scores = []
  G_losses= []

  d_optimizer = torch.optim.Adam(Discriminator.parameters(), lr=lr, betas=(0.5, 0.999))
  g_optimizer = torch.optim.Adam(Generator.parameters(), lr=lr, betas=(0.5, 0.999))

  for epoch in range(epochs):
    for i, batch in enumerate(trainload, 0):
      d_losses, d_real_scores, d_fake_scores = DiscriminatorTraining(batch, d_optimizer)
      g_losses = GeneratorTraining(g_optimizer)

      D_losses.append(d_losses)
      D_real_scores.append(d_real_scores)
      D_fake_scores.append(d_fake_scores)
      G_losses.append(g_losses)

    QuasiValidationSave(epoch+1, fixed_first_latentinput, show_gridimage=False)

    print("Epoch [{}/{}, d_losses {:.3f}, d_real_scores {:.3f}, d_fake_scores {:.3f}, g_losses {:.3f}]".format(epoch+1, epochs, d_losses, d_real_scores, d_fake_scores, g_losses))

  return D_losses, D_real_scores, D_fake_scores, G_losses

history = fit(trainload, 0.0002, 25)

torch.save(Discriminator.state_dict(), 'Discriminator.pth')
torch.save(Generator.state_dict(), 'Generator.pth')

Image('./gridimages/gridimage-number-025.png')   #quasivalidation_directory is ./gridimages

files = [os.path.join(quasivalidation_directory, file) for file in os.listdir(quasivalidation_directory) if 'gridimage-number' in file]
files.sort     #ანუ ჯერ ზევით ამოვაკოპირეთ ყველა შენახული სურათი და ყოველი შენთხვევისტვის აქ მაინც დავსორტეთ

videoname = 'results.avi'
video = cv2.VideoWriter(videoname, cv2.VideoWriter_fourcc(*'MPV4'), 1, (550, 550)) # 1 is framerate, (550, 550) dimensions
[video.write(cv2.imread(filename)) for filename in files]
video.release()

"""Use the following sources to find interesting datasets:

https://www.kaggle.com/datasets (use the opendatasets library for downloading datasets)
https://course.fast.ai/datasets
https://github.com/ChristosChristofidis/awesome-deep-learning#datasets
https://www.kaggle.com/competitions (check the "Completed" tab)
https://www.analyticsvidhya.com/blog/2018/03/comprehensive-collection-deep-learning-datasets/
https://lionbridge.ai/datasets/top-10-image-classification-datasets-for-machine-learning/
https://archive.ics.uci.edu/ml/index.php
https://github.com/awesomedata/awesome-public-datasets
https://datasetsearch.research.google.com/
Indian stocks data

https://nsepy.xyz/
https://nsetools.readthedocs.io/en/latest/usage.html
https://www.kaggle.com/rohanrao/nifty50-stock-market-data
Indian Air Quality Data

https://www.kaggle.com/rohanrao/air-quality-data-in-india
Indian Covid-19 Dataset

https://api.covid19india.org/
World Covid-19 Dataset

https://www.kaggle.com/imdevskp/corona-virus-report
USA Covid-19 Dataset

https://www.kaggle.com/sudalairajkumar/covid19-in-usa
Megapixels Dataset for Face Detection, GANs, Human Localization

https://megapixels.cc/datasets/ (Contains 7 different datasets)
Agriculture based dataset

https://www.kaggle.com/srinivas1/agricuture-crops-production-in-india
https://www.kaggle.com/unitednations/global-food-agriculture-statistics
https://www.kaggle.com/kianwee/agricultural-raw-material-prices-19902020
https://www.kaggle.com/jmullan/agricultural-land-values-19972017
India Digital Payments UPI

https://www.kaggle.com/lazycipher/upi-usage-statistics-aug16-to-feb20
India Consumption of LPG

https://community.data.gov.in/domestic-consumption-of-liquefied-petroleum-gas-from-2011-12-to-2017-18/
India Import/Export Crude OIl

https://community.data.gov.in/total-import-v-s-export-of-crude-oil-petroleum-products-by-india-from-2011-12-to-2017-18/
US Unemployment Rate Data

https://www.kaggle.com/jayrav13/unemployment-by-county-us
India Road accident Data

https://community.data.gov.in/statistics-of-road-accidents-in-india/
Data science Jobs Data

https://www.kaggle.com/sl6149/data-scientist-job-market-in-the-us
https://www.kaggle.com/jonatancr/data-science-jobs-around-the-world
https://www.kaggle.com/rkb0023/glassdoor-data-science-jobs
H1-b Visa Data

https://www.kaggle.com/nsharan/h-1b-visa
Donald Trump’s Tweets

https://www.kaggle.com/austinreese/trump-tweets
Hilary Clinton and Trump’s Tweets

https://www.kaggle.com/benhamner/clinton-trump-tweets
Asteroid Dataset

https://www.kaggle.com/sakhawat18/asteroid-dataset
Solar flares Data

https://www.kaggle.com/khsamaha/solar-flares-rhessi
Human face generation GANs

https://www.kaggle.com/arnaud58/flickrfaceshq-dataset-ffhq
F-1 Race Data

https://www.kaggle.com/cjgdev/formula-1-race-data-19502017
Automobile Insurance

https://www.kaggle.com/aashishjhamtani/automobile-insurance
PUBG

https://www.kaggle.com/skihikingkevin/pubg-match-deaths?
CS GO

https://www.kaggle.com/mateusdmachado/csgo-professional-matches
https://www.kaggle.com/skihikingkevin/csgo-matchmaking-damage
Dota 2

https://www.kaggle.com/devinanzelmo/dota-2-matches
Cricket

https://www.kaggle.com/nowke9/ipldata
https://www.kaggle.com/jaykay12/odi-cricket-matches-19712017
Basketball

https://www.kaggle.com/ncaa/ncaa-basketball
https://www.kaggle.com/drgilermo/nba-players-stats
Football

https://www.kaggle.com/martj42/international-football-results-from-1872-to-2017
https://www.kaggle.com/abecklas/fifa-world-cup
https://www.kaggle.com/egadharmawan/uefa-champion-league-final-all-season-19552019
"""
