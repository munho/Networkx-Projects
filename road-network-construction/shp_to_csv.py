#!/usr/bin/env python
# coding: utf-8
# jupyter nbconvert --to script shp_to_csv.ipynb

# #-*- coding: utf-8 -*-
# 
# ## From The standard Node-Link data to Network
# Data Source : http://nodelink.its.go.kr/data/data01.aspx
# 
# The standard node-link files consist of two kinds of shape files(node, link).
# 
# The _shapefile_ format is a popular geospatial vector data format for geographic information system (GIS) software. It is developed and regulated by Esri as a (mostly) open specification for data interoperability among Esri and other GIS software products. [wiki](https://en.wikipedia.org/wiki/Shapefile)
# 
# To construct network, we should modifiy shpfiles.

# In[60]:


import shapefile #the pyshp module : Should install pyshp module.
import pandas as pd
from pyproj import Proj, transform # Should install pyproj module.
import networkx as nx


# If you see an error message that `No module named modulename`, you should install module. To resolve this problem, we need to istall 'pyshp' and 'pyproj'. To do this, we use `pip`. We can install module easily by typing `pip install modulename`. To install `pyshp` and `pyproj`, we type the below codes in `terminal` or `anaconda prompt`.
# 
# ```
# pip install pyshp
# pip install pyproj
# ```
# If there is a problem to install pyproj, then do the following; conda install -c anaconda pyproj 

# ## Construct dataframe by using shp file

# In[61]:


# read data (Copy all files from nodelink into nodelink folder: I made it.)
# using old_data
shp_path_node = './nodelink_150105/MOCT_NODE.shp'
sf_node = shapefile.Reader(shp_path_node, encoding='cp949')
shp_path_link = './nodelink_150105/MOCT_LINK.shp'
sf_link = shapefile.Reader(shp_path_link, encoding='cp949')


# In[62]:


print (' construct pandas dataframe')

#grab the shapefile's field names
# node
fields_node = [x[0] for x in sf_node.fields][1:]
records_node = sf_node.records()
shps = [s.points for s in sf_node.shapes()] # node has coordinate data.
# link
fields_link = [x[0] for x in sf_link.fields][1:]
records_link = sf_link.records()


#write the records into a dataframe
# node
node_dataframe = pd.DataFrame(columns=fields_node, data=records_node)
#add the coordinate data to a column called "coords"
node_dataframe = node_dataframe.assign(coords=shps)
# link
link_dataframe = pd.DataFrame(columns=fields_link, data=records_link)


# ''' Show the files'''

# In[63]:


node_dataframe[1:5]# Show first 5 items.


# Show the file with only if STNL_REG=333/ here "333" is assigned as a string

# In[64]:


node_dataframe[node_dataframe['STNL_REG'] == str(333)][1:5]


# We observe that **NODE_NAME**, **ROAD_NAME** are not string and **coords** is strange coordinate system. We will fix later.
# 
# Now, we restirct data for some city before we fix.

# <img src="https://trello-attachments.s3.amazonaws.com/59103d52b56a24582f00dc97/5ac8b77017464fe59d4b728e/6388818a77f59b02e011068d58dc8145/image.png"></img>

# ![image.png](attachment:image.png)

# http://nodelink.its.go.kr/intro/intro06_05.aspx
# Please find more info from nodelink site
# 
# **광역/특별시의 권역코드 (STNL_REG)**
# - 서울 : 100 ~ 124
# - 부산 : 130 ~ 145
# - 대구 : 150 ~ 157
# - 인천 : 161 ~ 170
# - 광주 : 175 ~ 179
# - 대전 : 183 ~ 187
# - 울산 : 192 ~ 196

# **In this code, we choose Incheon.**

# In[65]:


node_dataframe.dtypes # Check data types of columns.


# In[66]:


print (' Data restriction')
range_STNL_REG=range(161,170) # STNL_REG for Incheon
df_node = pd.DataFrame()
df_link = pd.DataFrame()
for ii in range_STNL_REG:
    res_node = node_dataframe[node_dataframe['STNL_REG'] == str(ii) ] # STNL_REG is not int.
    res_link = link_dataframe[link_dataframe['STNL_REG'] == str(ii) ]
    df_node = pd.concat([df_node,res_node],ignore_index=True) # marge data
    df_link = pd.concat([df_link,res_link],ignore_index=True)


# In[67]:


# print ('Change node name in korean')
# for idx,row in df_node.iterrows():
#     if type(row['NODE_NAME']) == bytes: # <-- <type 'unicode'>
#         # row['NODE_NAME'] = row['NODE_NAME'].decode('euc_kr')
#         # row['NODE_NAME'] = row['NODE_NAME'].decode('cp949')
#         print("idx={} row['NODE_NAME']={}".format(idx, row['NODE_NAME']))
#         row['NODE_NAME'] = row['NODE_NAME'].decode('utf8')


# In nodelink data, all positions in nodes are assigned based on **korea 2000 좌표계**. Their positions are changed based on 
# **wgs84 (위도/경도)** by using Proj package.

# In[68]:


print (' Change coordinate system')
print (' korea 2000/central belt 2010 (epsg:5186) to wgs84(epsg:4326)')
inProj = Proj(init = 'epsg:5186')
outProj= Proj(init = 'epsg:4326')
latitude = []
longitude= []
for idx,row in df_node.iterrows():
    x,y  = row.coords[0][0],row.coords[0][1]  # korea 2000 좌표계
    nx,ny = transform(inProj,outProj,x,y)     # 새로운 좌표계    
    latitude.append(ny)
    longitude.append(nx)
df_node['latitude'] = latitude
df_node['longitude']= longitude
del df_node['coords'] # delete coords


# In order to use Gephi, it is essential to have two files node and line file. Also each one has a special properties. That is, node name has to be indexed as an **ID** and link has two names **Source** and **Target**. File in below show that how to change the given form to gephi-type file form.

# In[69]:


print (' Change column name to draw network in Gephi')
df_node.rename(columns={'NODE_ID':'Id'},inplace = True)
df_link.rename(columns={'F_NODE':'Source','T_NODE':'Target'},inplace = True)


# In[70]:


print("len(df_node)= " + str(len(df_node)))


# In[71]:


df_node.head()


# In[72]:


df_link[1:5]


# # You can save Data as csv formet.

# In[73]:


df_node.to_csv('Incheon_nodes_150105.csv', encoding='cp949') # node list
df_link.to_csv('Incheon_links_150105.csv', encoding='cp949') # edge(=link) list


# In[ ]:


df_link.columns


# In[ ]:





# In[ ]:




