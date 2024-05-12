import numpy as np
from matplotlib.figure import Figure
import imageio
import os
import networkx as nx
from gensim.models import Word2Vec
from node2vec import Node2Vec
from sklearn.metrics.pairwise import cosine_similarity
from skimage.transform import resize
import cv2


def calculate_histogram(image):
    image = image.astype('uint8')
    blue_channel = image[:,:,0]
    green_channel = image[:,:,1]
    red_channel = image[:,:,2]
    
    blue_hist = cv2.calcHist([blue_channel], [0], None, [256], [0, 256]) 
    green_hist = cv2.calcHist([green_channel], [0], None, [256], [0, 256]) 
    red_hist = cv2.calcHist([red_channel], [0], None, [256], [0, 256]) 
    
    return blue_hist, green_hist, red_hist

def compare_histograms(hist1, hist2):
    bhattacharyya = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
    return bhattacharyya

def compare_patches(patch1 , patch2):
    blue_color1, green_color1, red_color1 = calculate_histogram(patch1)
    blue_color2, green_color2, red_color2 = calculate_histogram(patch2)


    bhattacharyya_blue = compare_histograms(blue_color1, blue_color2)
    bhattacharyya_green = compare_histograms(green_color1, green_color2)
    bhattacharyya_red = compare_histograms(red_color1, red_color2)


    overall_similarity = (bhattacharyya_blue + bhattacharyya_green + bhattacharyya_red) / 3
    return overall_similarity

def generate_patches(image, num_patches):
    img_height, img_width, _ = image.shape
    

    patch_size = int(np.sqrt((img_height * img_width) / num_patches))
    
    overlap = patch_size // 2

    patches = []

    for i in range(num_patches):
        row_idx = i // (num_patches ** 0.5)
        col_idx = i % (num_patches ** 0.5)   
        
        start_row = int(row_idx * (patch_size - overlap))
        end_row = start_row + patch_size
        start_col = int(col_idx * (patch_size - overlap))
        end_col = start_col + patch_size

        patch = image[start_row:end_row, start_col:end_col, :]
        patches.append(patch)

    patch_dict = {'P' + str(i + 1): patches[i] for i in range(num_patches)}

    return patch_dict

def createGraph(patchDict):
  GraphImage = nx.Graph()
  for key in patchDict:
      GraphImage.add_node(key)

  for key1 in patchDict:
      for key2 in patchDict:
          if key1 != key2:
              intersection = compare_patches(patchDict[key1], patchDict[key2])
              GraphImage.add_edge(key1, key2, weight=intersection)

  print("Nodes in GraphImage:")
  for node in GraphImage.nodes():
      print(node)

  print("Edges in GraphImage with weights and intersection:")
  for edge in GraphImage.edges(data=True):
      print(edge)
      
  return GraphImage



def displayGraph(GraphImage, graph_name):
    fig = Figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    pos2 = nx.spring_layout(GraphImage)
    nx.draw(GraphImage, pos=pos2, with_labels=True, node_color='lightgreen', node_size=1500, font_size=10, font_weight='bold', ax=ax)
    nx.draw_networkx_edge_labels(GraphImage, pos=pos2, font_color='blue', ax=ax)
    ax.set_title(graph_name)

    save_path = 'project/static/graphs'

    filename = f'{graph_name.replace(" ", "_").lower()}.png'  
    fig.savefig(os.path.join(save_path, filename)) 

\

def convertComparable(graph_data):
    graph = nx.Graph()
    for edge in graph_data.edges(data=True): 
        source = str(edge[0])
        target = str(edge[1])
        weight = edge[2]['weight'] if 'weight' in edge[2] else 1 
        graph.add_edge(source, target, weight=weight) 
    return graph
    
def checkSimilarity():
    dir_path = "project/static/uploads"
    file_list = os.listdir(dir_path)
    file_list = [os.path.join(dir_path, file) for file in file_list]
    img1 = imageio.imread(file_list[0])
    img2= imageio.imread(file_list[1])
    ImgDict1 = generate_patches(img1,6)
    ImgDict2 = generate_patches(img2,6)
    ImgG1 = createGraph(ImgDict1)
    ImgG2 = createGraph(ImgDict2)
    displayGraph(ImgG1, 'GraphImage1')
    displayGraph(ImgG2, 'GraphImage2')
    GraphImage1_nx = convertComparable(ImgG1)
    GraphImage2_nx = convertComparable(ImgG2)
    combinedGraph = nx.compose(GraphImage1_nx, GraphImage2_nx)
    node2vec = Node2Vec(combinedGraph, dimensions=64, walk_length=30, num_walks=200, workers=4)
    model = node2vec.fit(window=10, min_count=1, batch_words=4)
    graph1_embeddings = np.array([model.wv[str(node)] for node in GraphImage1_nx.nodes()])
    graph2_embeddings = np.array([model.wv[str(node)] for node in GraphImage2_nx.nodes()])
    similarity_matrix = cosine_similarity(graph1_embeddings, graph2_embeddings)
    average_similarity = np.mean(similarity_matrix)*10
    retLine = "Average similarity score between GraphImage1 and GraphImage2: {:.2f} %".format(average_similarity * 10)
    return retLine
    
    
    
    