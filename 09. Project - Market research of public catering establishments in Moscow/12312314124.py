#!/usr/bin/env python
# coding: utf-8

# # Проект: Исследование рынка заведений общественного питания Москвы 

# **Требуется подготовить исследование рынка Москвы, найти интересные особенности и презентовать полученные результаты, которые в будущем помогут в выборе подходящего инвесторам места.**

# # План работы:

# 1. Подготовка к работе
#     1. Выведем таблицы и изучим данные
# 2. Предобработка данных
#     1. Проверка на дубликаты
#     2. Проверка на пропуски
#     3. Создание столбца street с названием улиц
#     4. Сздание столбца is24_7 с обозначением, что заведение работает 24 на 7
# 3.	Анализ данных
#     1. Исследуем виды объектов общественного питания.
#     2. Исследуем количество посадочных мест по категориям.
#     3. Исследуем соотношение сетевых и не сетевых заведений.
#     4. Расмотрим соотношение сетевых и несетевых магазинов по категориям.
#     5. Сгруппируем данные по названиям заведений и найдем топ-15.
#     6. Проверим в каких административных районах Москвы присутствуют заведения.
#     7. Распределим средний рейтинг по категориям и визуализируем.
#     8. Построим фоновую картограмму (хороплет).
#     9. Отобразим все заведения на карте при помощи кластеров.
#     10. Найдем Топ-15 улиц по каличеству заведений.
#     11. Посчитаем медиану чека по каждому району.
#     12. Общий вывод исследования.
# 4.  Детализация иследонваия: открытие кофейни
#     1. Сколько всего кофеен в датасете? В каких районах их больше всего, каковы особенности их расположения?
#     2. Есть ли круглосуточные кофейни? 
#     3. Какие у кофеен рейтинги? Как они распределяются по районам?
#     4. На какую стоимость чашки капучино стоит ориентироваться при открытии и почему?
#     5. Сколько сетей в категории кофейни?
#     6. Рекомедации.
# 5. Презентация
#     

# ## Подгатовка к работе

# ### Выведем таблицы и изучим данные

# In[1]:


import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium import Map, Choropleth, Marker
from folium.plugins import MarkerCluster


# In[2]:


# снимем ограничение на ширину столбцов
pd.set_option('display.max_colwidth', None)
# снимаем ограничение на количество столбцов
pd.set_option('display.max_columns', None)


# In[3]:


data = pd.read_csv('/datasets/moscow_places.csv')


# In[4]:


data.info()


# In[5]:


data.head(5)


# **В данных представлено информация о 8406-ти разнообразных, от самых малых до огромных сетевых, точках общественного питания в Москве.**

# ## Предобработка данных

# ### Проверка на дубликаты

# In[6]:


data.duplicated().sum()


# **Проверим на не явные дубликаты**

# Столбец котегорий общепитов

# In[7]:


data.category.unique()


# Дубликатов не выявлено

# Столбец районов

# In[8]:


data.district.unique()


# Дубликатов не выявлено
# 
# Остальные столбцы нету смысла проверять, там может быть очень много разных значений

# ### Проверка на пропуски

# In[9]:


data.isna().sum()


# **В первую очередь проверим столбец с информацией о днях и часах работы**

# In[10]:


data.query('hours.isna()').head(5)


# **Столбец с категорией цен**

# In[11]:


data.query('price.isna()').head(5)


# Столбец хронящий среднюю стоймость заказа

# In[12]:


data.query('avg_bill.isna()').head(5)


# Столбец с оценкой среднего чека

# In[13]:


data.query('middle_avg_bill.isna()').head(5)


# Столбец с оценкой средней цены за чашку капучино

# In[14]:


data.query('middle_coffee_cup.isna()').head(5)


# Столбец с количеством посадочных месть

# In[15]:


seats = data.query('seats.isna()')
seats.head(5)


# **Вывод:** В данных есть пропуски, но они скорее всего были не заполнена из-за недостатков данных о заведениях. Заполнить или удалить из таблицы не составляет возможным, т.к. при удаление будет искажено само исследование.
# 
# Столбцы middle_avg_bill и middle_coffee_cup, они на прямую зависят от столбца avg_bill, и могут быть заполнен либо один, либо другой.
# 

# ### Создание столбца street с названием улиц

# Выведем улицу в отдельную колонку. К сожалению, часть названий улиц будет обработано некорректно из-за различий в написании адреса.

# In[16]:


data['street']=data['address'].apply(lambda x:x.split(',')[1])


# In[17]:


data.head(5)


# ### Сздание столбца is24_7  с обозначением, что заведение работает 24 на 7

# Логическое значение True — если заведение работает ежедневно и круглосуточно;
# 
# Логическое значение False — в противоположном случае.

# In[18]:


data['is24_7'] = data['hours'].str.contains('ежедневно, круглосуточно')


# In[19]:


data.head(5)


# ## Анализ данных

# ### Исследуем виды объектов общественного питания

# In[20]:


data_category = (data
                .groupby('category')
                .agg(count=('name','count'))
                .reset_index()
                .sort_values('count', ascending=False)
                )
data_category['percent'] = (data_category['count'] / sum(data_category['count']) * 100).round(2)


# In[21]:


data_category


# In[22]:


fig= px.bar(data_category, x='category', y='count', title='Соотношение объектов по категориям')
fig.update_xaxes(tickangle=45)
fig.update_xaxes(title_text='Категория')
fig.update_yaxes(title_text='Кол-во объектов')
fig.show() 


# **Вывод:** В лидерах категории кафе (28%) и рестораны (24%), на третьем месте кофейни (16,8%). Меньше всего в городе представлены булочные (3%).

# ### Исследуем количество посадочных мест по категориям 

# In[23]:


data_category = (data
                .groupby('category')
                .agg(mean=('seats', 'mean'), count=('seats', 'count'))
                .reset_index()
                .sort_values('mean', ascending=False)
                )
data_category['mean']=data_category['mean'].round(0)


# In[24]:


data_category


# In[25]:


#Заведения с самыми большими залами
data.seats.max()


# In[26]:


plt.figure(figsize=(12, 7))
sns.boxplot(x='seats', y='category', data=data, hue='chain', palette='Pastel2')
plt.xlim(-5,600)
plt.title('РАСПРЕДЕЛЕНИЕ КОЛИЧЕСТВА ПОСАДОЧНЫХ МЕСТ ПО КАТЕГОРИЯМ (СЕТЕВЫЕ/НЕСЕТЕВЫЕ)')
plt.xlabel('Количество мест')
plt.ylabel('')
plt.show()


# **Вывод:** Как мы видим, самое большое количество посадочных мест - у бар/паб и ресторанов. В сетевых магазинах как правило в среднем больше посадочных мест в заведении чем несетевых.

# ### Исследуем соотношение сетевых и не сетевых заведений

# In[27]:


data_chain = data.groupby('chain').agg(count=('name','count')).reset_index()
plt.figure(figsize=(10, 10))
plt.pie(data_chain['count'],
        labels=data_chain['chain'].map({True: 'СЕТЕВЫЕ ЗАВЕДЕНИЯ', False: 'НЕСЕТЕВЫЕ МАГАЗИНЫ'}), 
        counterclock=False,
        colors = ['#4682B4', '#00BFFF'],
        explode = (0.1, 0),
        autopct='%1.1f%%',
        shadow=True)
plt.title('СООТНОШЕНИЕ СЕТЕВЫХ И НЕСЕТЕВЫХ ЗАВЕДЕНИЙ')
plt.show()


# **Вывод:** Более 61% заведений несетевые. 

# ### Расмотрим соотношение сетевых и несетевых магазинов по категориям

# In[28]:


data_chain_category  = data.pivot_table(
    index = 'category',
    columns = 'chain',
    values = 'name',
    aggfunc='count'
).rename(columns={True: 'network', False: 'not_network'}).sort_values(by='network', ascending=True).reset_index()
data_chain_category['percent'] = (data_chain_category['network']
                                  /(data_chain_category['network']
                                  +data_chain_category['not_network'])*100).round(1)
data_chain_category = data_chain_category.sort_values(by='percent', ascending=False)
data_chain_category


# In[29]:


fig= px.bar(data_chain_category, x='category', y='percent', title='% сетевых от общего количества каждого типа')
fig.update_xaxes(tickangle=45)
fig.update_xaxes(title_text='Категория')
fig.update_yaxes(title_text='Доля')
fig.show() 


# **Вывод:** Фактически во всех категория преобладают несетевые заведения и только три категории отличаются. В категории булочная, пиццерия и кофейни преобладают сети.

# ### Сгруппируем данные по названиям заведений и найдем топ-15

# In[30]:


group_name = (data.query('chain == 1').groupby('name')
              .agg(count=('name','count')).sort_values(by='count', ascending=False).reset_index()
             )


# In[31]:


group_name = group_name.head(15)
group_name


# In[32]:


fig=px.bar(group_name, x='count', y='name', title='Топ-15 сетевых заведений в Москве')
fig.update_xaxes(tickangle=45)
fig.update_xaxes(title_text='Кол-во заведений')
fig.update_yaxes(title_text='')
fig.show() 


# С большим отрывом лидирует сеть кофейни «Шоколадница». Замыкает Топ-15 заведение «Му-Му». В лидерах сети очень знаменитые и везде на слуху.

# In[33]:


list_group_name = group_name['name'].tolist()
top_15_category = (data.query('name in @list_group_name')
                   .groupby('name').agg(category=('category','max')).reset_index())
top_15_category


# In[34]:


(top_15_category.groupby('category')
 .agg(count=('category','count')).sort_values(by='count', ascending=False).reset_index())


# In[35]:


fig=px.bar((top_15_category.groupby('category')
            .agg(count=('category','count'))
            .sort_values(by='count', ascending=False).
            reset_index()), 
           x='category', y='count', title='Категории к кторым относятся Топ-15 сетей')
fig.update_xaxes(title_text='Категория')
fig.update_yaxes(title_text='Кол-во заведений')
fig.show() 


# **Вывод:** Самая популярная сеть, - это кофейня «Шоколадница». Все сети Топ-15 очень знаменитые и везде на слуху. В основном крупные сети относятся к категориям: Кофейня, Ресторан и пиццерия.

# ### Проверим в каких административных районах Москвы присутствуют заведения 

# In[36]:


data.district.unique()


# In[37]:


data_district = (data.groupby('district')
                .agg(count=('name','count'))
                .sort_values(by='count', ascending=False).
                reset_index())


# In[38]:


data_district


# In[39]:


fig=px.bar(data_district, x='district', y='count', title='Административные районы Москвы')
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='Кол-во заведений')
fig.show() 


# На графике видим, что в центральном районе Москвы расположилось очень много заведений

# In[40]:


data_district_category = (data.groupby(['district', 'category'])
                .agg(count=('name','count'))
                .sort_values(by='count', ascending=False).
                reset_index())


# In[41]:


data_dis_cat = (data_district_category.groupby(['district'])
                .agg(sum=('count','sum'))
                .sort_values(by='sum', ascending=False).
                reset_index())
data_dis_cat


# In[42]:


data_district_category = data_district_category.merge(data_dis_cat, how="left")
data_district_category['percent'] =  (data_district_category['count']/data_district_category['sum']*100).round(2)
data_district_category


# In[43]:


fig = px.bar(data_district_category, x='percent', y='district'
             , color='category', text='percent', title='Распредиление заведений в разрезе категорий по округам')
fig.update_xaxes(title_text='%')
fig.update_yaxes(title_text='')
fig.show()


# **Вывод:** В центральном округе преобладают Рестораны, кафе и кофейни. Основное количество заведений расположена в ЦАО. Меньше всего общепита в СЗАО.

# ### Распределим средний рейтинг по категориям и визуализируем

# In[44]:


data_rating = data.groupby('category').agg(rating=('rating', 'mean')).sort_values(by='rating', ascending=False).reset_index()
data_rating


# In[45]:


plt.figure(figsize=(14,6))
plt.bar(x = data_rating.category, height = data_rating.rating)
plt.ylim([4, 4.5])
plt.xticks(rotation = 75)
plt.title('График - Средний рейтинг по категориям')
plt.show()


# **Вывод:** Самый высокий рейтинг у баров и пабов, видимо потому что в этих заведениях по минимуму берут еду, а в основном алкоголь и снеки. Самый низкий рейтинг у быстрого питания. 

# ### Построим фоновую картограмму (хороплет)

# In[46]:


rating_data =  data.groupby('district', as_index=False)['rating'].agg('mean')
rating_data


# In[47]:


# загружаем JSON-файл с границами округов Москвы
state_geo = '/datasets/admin_level_geomap.geojson'
# moscow_lat - широта центра Москвы, moscow_lng - долгота центра Москвы
moscow_lat, moscow_lng = 55.751244, 37.618423

# создаём карту Москвы
m = Map(location=[moscow_lat, moscow_lng], zoom_start=10)

# создаём хороплет с помощью конструктора Choropleth и добавляем его на карту
Choropleth(
    geo_data=state_geo,
    data=rating_data,
    columns=['district', 'rating'],
    key_on='feature.name',
    fill_color='YlOrBr',
    fill_opacity=0.8,
    legend_name='Медианный рейтинг заведений по районам',
).add_to(m)

# выводим карту
m


# **Вывод:** Наглядно видно, что самые высокие рейтинги в ЦАО

# ### Отобразим все заведения на карте при помощи кластеров

# In[48]:


moscow_lat, moscow_lng = 55.751244, 37.618423

# создаём карту Москвы
m = Map(location=[moscow_lat, moscow_lng], zoom_start=10)
# создаём пустой кластер, добавляем его на карту
marker_cluster = MarkerCluster().add_to(m)

# пишем функцию, которая принимает строку датафрейма,
# создаёт маркер в текущей точке и добавляет его в кластер marker_cluster
def create_clusters(row):
    Marker(
        [row['lat'], row['lng']],
        popup=f"{row['name']} {row['rating']}",
    ).add_to(marker_cluster)

# применяем функцию create_clusters() к каждой строке датафрейма
data.apply(create_clusters, axis=1)

# выводим карту
m


# **Вывод:** Кластеры облегчают работу карты, более 8000 заведений поместили на карту и она стабильно работает

# ### Найдем Топ-15 улиц по каличеству заведений

# In[49]:


data_str = (data.groupby('street')
            .agg(sum=('name', 'count')).sort_values(by='sum', ascending=False).reset_index())
data_str = data_str.head(15)
data_str


# In[50]:


fig = px.bar(data_str, x='street', y='sum', title='Топ-15 улиц')
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='Кол-во заведений')
fig.show()


# In[51]:


data_street = (data.pivot_table(index ='street', columns = 'category', values = 'name', aggfunc = 'count')
 .sort_values(ascending=False, by = 'street'))
data_street = data_street.query('street in @data_str["street"]')


# In[52]:


data_street = (data.groupby(['street', 'category'])
               .agg(count=('name', 'count'))
               .sort_values(by='count', ascending=False)
               .reset_index())
data_street = data_street.merge(data_str, how="left")
data_street['percent'] =  (data_street['count']/data_street['sum']*100).round(2)
data_street = data_street.query('street in @data_str["street"]')
data_street


# In[53]:


fig = px.bar(data_street, x='percent', y='street'
             , color='category', text='percent', title='Распредиление заведений в разрезе категорий по округам')
fig.update_xaxes(title_text='%')
fig.update_yaxes(title_text='')
fig.show()


# **Вывод:** На улице мира расположилось больше всего заведений общественного питания, а именно Кафе. 

# In[54]:


data_street_one = data.groupby('street').agg(count=('name', 'count')).sort_values(by='count', ascending=False).reset_index()
data_street_one = data_street_one.query('count == 1' )
data_street_one.head(15)


# In[55]:


print ('Всего улиц с одни заведением:', data_street_one['street'].count())


# In[56]:


data_street_one_map = data.query('street in @data_street_one["street"]')


# In[57]:


moscow_lat, moscow_lng = 55.751244, 37.618423

# создаём карту Москвы
m = Map(location=[moscow_lat, moscow_lng], zoom_start=10)
# создаём пустой кластер, добавляем его на карту
marker_cluster = MarkerCluster().add_to(m)

# пишем функцию, которая принимает строку датафрейма,
# создаёт маркер в текущей точке и добавляет его в кластер marker_cluster
def create_clusters(row):
    Marker(
        [row['lat'], row['lng']],
        popup=f"{row['name']} {row['rating']}",
    ).add_to(marker_cluster)

# применяем функцию create_clusters() к каждой строке датафрейма
data_street_one_map.apply(create_clusters, axis=1)

# выводим карту
m


# **Вывод:** Лидирует Центральный административный округ с его маленькими уютными улочками.

# ### Посчитаем медиану чека по каждому району

# In[58]:


data_avg_bill = data.groupby('district').agg(median=('middle_avg_bill', 'median')).sort_values(by='median', ascending=False).reset_index()
data_avg_bill


# In[59]:


# загружаем JSON-файл с границами округов Москвы
state_geo = '/datasets/admin_level_geomap.geojson'
# moscow_lat - широта центра Москвы, moscow_lng - долгота центра Москвы
moscow_lat, moscow_lng = 55.751244, 37.618423

# создаём карту Москвы
m = Map(location=[moscow_lat, moscow_lng], zoom_start=10)

# создаём хороплет с помощью конструктора Choropleth и добавляем его на карту
Choropleth(
    geo_data=state_geo,
    data=data_avg_bill,
    columns=['district', 'median'],
    key_on='feature.name',
    fill_color='YlOrBr',
    fill_opacity=0.8,
    legend_name='Медианный рейтинг заведений по районам',
).add_to(m)

# выводим карту
m


# **Вывод:** Самые дорогие заведения находятся в ЦАО и ЗАО. С центром все понятно, туда съезжаются все и понятное дело там самые высокие цены. В ЗАО средник чек высок как в центре, скорее всего там живут более состоятельные люди чем в других округах.

# ### Общий вывод исследования

# **Типы объектов общественного питания:**
# 
#     •	Кафе - самое распространённое заведение общественного питания: около 28% всех точек относятся к данному типу;
#     •	Далее по численности идут рестораны (24%) и кофейни (16%);
#     •	Меньше всего в Москве столовых (3,75%) и булочных (3,05%);
# 
# **Сетевые заведения:**
# 
#     •	38 % заведений общественного питания являются сетевыми;
#     •	Типичный представитель сетевого заведения - Кафе;
#     •	Достаточно широко представлены рестораны и кофейни;
#     •	Самая популярная сеть, - это кофейня «Шоколадница;
# 
# **Посадочные места:**
# 
#     •	в Москве представлены заведения с широким диапазоном посадочных мест (начиная от их полного отсутствия в закусочных и магазинах и заканчивая огромными банкетными залами на 1288 посадочных мест);
#     •	Если не впадать в крайности, то список посадочных мест по убыванию в заведениях выглядит так: бары и пабы (среднее кол-во мест 125) и рестораны (122), кофейни (111) и столовые (100);
# 
# **Расположение объектов общественного питания:**
# 
#     •	Самое большое количество улиц с единственным заведением находится в ЦАО; впрочем, как, большинство заведений так же располагается в ЦАО;
#     •	Заведения с самыми высокими рейтингами находятся в ЦАО;
#     •	Заведения с высокой стоимостью среднего чека находятся в ЦАО и ЗАО;
#     •	На улице мира расположилось больше всего заведений общественного питания, а именно Кафе;
# 

# ## Детализация иследонваия: открытие кофейни

# Отметим на вопросы основателей фонда, которые хотят открыть кофейню, такую же крутую как “Central Park” из сериала друзья.

# ### Сколько всего кофеен в датасете? В каких районах их больше всего, каковы особенности их расположения?

# In[60]:


data_coffee = data.query('category == "кофейня"')
print ('Всего кофеен в датасете:', data.query('category == "кофейня"')['name'].count())


# In[61]:


data_cf = (data_coffee.groupby('district')
                .agg(count=('name','count'))
                .sort_values(by='count', ascending=False).
                reset_index())
fig = px.bar(data_cf, x='district', y='count', title='Расположение кофеен по районам')
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='Кол-во заведений')
fig.show()


# In[62]:


moscow_lat, moscow_lng = 55.751244, 37.618423

# создаём карту Москвы
m = Map(location=[moscow_lat, moscow_lng], zoom_start=10)
# создаём пустой кластер, добавляем его на карту
marker_cluster = MarkerCluster().add_to(m)

# пишем функцию, которая принимает строку датафрейма,
# создаёт маркер в текущей точке и добавляет его в кластер marker_cluster
def create_clusters(row):
    Marker(
        [row['lat'], row['lng']],
        popup=f"{row['name']} {row['rating']}",
    ).add_to(marker_cluster)

# применяем функцию create_clusters() к каждой строке датафрейма
data_coffee.apply(create_clusters, axis=1)

# выводим карту
m


# Больше все кофеен расположена в ЦАО, как правило основные клиенты — это работники ближайших офисов, которые каждый день, ходят на работу и с утра заходят в кофейню чтобы выпить ободряющую чашечку кофе и съесть завтрак, ну и просто люди которые приехали в центр Москвы на прогулку

# ### Есть ли круглосуточные кофейни?

# In[63]:


print ('Кофеен с круглосуточным режимом работы:', data_coffee.query('is24_7 == True')['name'].count())


# In[64]:


data_coffee24 = data_coffee.query('is24_7 == True')
data_cf24 = (data_coffee24.groupby('district')
                .agg(count=('name','count'))
                .sort_values(by='count', ascending=False).
                reset_index())
fig = px.bar(data_cf24, x='district', y='count', title='Расположение круглосуточных кофеен по районам')
fig.update_xaxes(title_text='')
fig.update_yaxes(title_text='Кол-во заведений')
fig.show()


# ### Какие у кофеен рейтинги? Как они распределяются по районам?

# In[65]:


rating_coffee =  data_coffee.groupby('district', as_index=False)['rating'].agg('mean').sort_values(by='rating', ascending=False)
rating_coffee


# In[66]:


plt.figure(figsize=(14,6))
plt.bar(x = rating_coffee.district, height = rating_coffee.rating)
plt.ylim([4.1, 4.4])
plt.title('Рейтинг кофеен по районам')
plt.xticks(rotation = 75)
plt.show()


# In[67]:


# загружаем JSON-файл с границами округов Москвы
state_geo = '/datasets/admin_level_geomap.geojson'
# moscow_lat - широта центра Москвы, moscow_lng - долгота центра Москвы
moscow_lat, moscow_lng = 55.751244, 37.618423

# создаём карту Москвы
m = Map(location=[moscow_lat, moscow_lng], zoom_start=10)

# создаём хороплет с помощью конструктора Choropleth и добавляем его на карту
Choropleth(
    geo_data=state_geo,
    data=rating_coffee,
    columns=['district', 'rating'],
    key_on='feature.name',
    fill_color='YlOrBr',
    fill_opacity=0.8,
    legend_name='Медианный рейтинг заведений по районам',
).add_to(m)

# выводим карту
m


# Рейтинги у кофеен разные от 4.19 до 4,33. Самые высокие рейтинги в Центральном и Северо-Западном округе.

# ### На какую стоимость чашки капучино стоит ориентироваться при открытии и почему?

# In[68]:


data_cent = (data_coffee.groupby('district')
                .agg(median=('middle_coffee_cup','median'))
                .sort_values(by='median', ascending=False).
                reset_index())
data_cent


# In[69]:


# загружаем JSON-файл с границами округов Москвы
state_geo = '/datasets/admin_level_geomap.geojson'
# moscow_lat - широта центра Москвы, moscow_lng - долгота центра Москвы
moscow_lat, moscow_lng = 55.751244, 37.618423

# создаём карту Москвы
m = Map(location=[moscow_lat, moscow_lng], zoom_start=10)

# создаём хороплет с помощью конструктора Choropleth и добавляем его на карту
Choropleth(
    geo_data=state_geo,
    data=data_cent,
    columns=['district', 'median'],
    key_on='feature.name',
    fill_color='YlOrBr',
    fill_opacity=0.8,
    legend_name='Медианный рейтинг заведений по районам',
).add_to(m)

# выводим карту
m


# Стоимость чашки кофе будет завесить от выбранного для кофейни округа, так к примеру, самая дорогая средняя стоимость чаши в Юго-Западном административном округе она составляет 198 руб. на втором месте ЦАО там средняя стоимость 190 руб. Самая дешёвая стоимость чашки кофе в восточном административном округе (135 руб.).

# ### Сколько сетей в категории кофейни?

# In[70]:


group_nam_coffee = (data_coffee.query('chain == 1').groupby('name')
              .agg(count=('name','count'))
                    .sort_values(by='count', ascending=False).reset_index()
             )
print ('Всего сетевых магазинов в категории кофейни:', group_nam_coffee['name'].count())


# In[71]:


group_nam_coffee = group_nam_coffee.head(15)
fig=px.bar(group_nam_coffee, x='name', y='count', title='Топ-15 сетевых кофеен в Москве')
fig.update_xaxes(tickangle=45)
fig.update_xaxes(title_text='Сеть')
fig.update_yaxes(title_text='Кол-во заведений')
fig.show() 


# **Вывод:** Самые крупная сеть общественного питания  расположились в категории кофейни.  Всего же в категории кофеен, 159 сетей. Самая крупная, это сеть Шоколадница.

# ### Рекомендации
# В ходе исследования мы выяснили, что кофейня - это одно из самых перспективных вариантов среди заведений общественного питания (16% находился на 3-м месте после кофе и ресторанов). Среднее количество посадочных мест - 111. Наибольшее количество существующих заведений сосредоточено в ЦАО.
# 
# С учетом специфики будущего заведения - основной целевой аудиторией видятся работники ближайших офисов и прогуливающиеся люди по улочкам Москвы. В таком месте получаются отличные селфи с кофе, которые не стыдно показать друзьям и коллегам по работе.
# 
# В качестве локации рекомендуем обратить внимание на улицах ЦАО, где ни будь в деловом центре. Центр - это всегда улицы с высокой проходимостью и большое количество разных людей и туристов. Конечно в центре и конкуренция выше, но с учетом высокого трафик людей будет необходимое количество посетителей. И вероятность, что поток клиентов иссякнет – маловероятен. В части масштабирования с учетом спецификации будущего заведения, оптимальным вариантом будет создать сет из нескольких точек в 3-4 округах города. Т.к. постоянный клиент с картой лояльность от вашей сети будет искать именно ваше заведение. 
# 

# ## Презентация
# 
# Презентация: https://disk.yandex.ru/i/VOlGvQ8xU4fjYg
# 
