



![image](/README_files/img/01_main_logo.png)



# 프로젝트 소개

> 🥕 **오늘의 레시피**는 개인 맞춤형 레시피 추천 서비스입니다



![image](/README_files/img/02_오늘의레시피_main.png)

## Link

> 오늘의 레시피 - [http://115.85.182.72:30005/](http://115.85.182.72:30005/)
> 
> Github -  [https://github.com/boostcampaitech5/level3_recsys_finalproject-recsys-10/](https://github.com/boostcampaitech5/level3_recsys_finalproject-recsys-10/)
>
> 발표자료 - [link](/README_files/[ppt]%20오늘의%20레시피_I-Five.pdf)
>
> WrapUp report - [link](/README_files/Recsys-10%20|%20[오늘의%20레시피]%20개인화%20레시피%20추천%20서비스%20|%20WrapUp%20report.pdf)

## 프로젝트 배경

![image](/README_files/img/03_프로젝트배경.png)

> 기존의 레시피 사이트들은 유저 조회수나 평점에 의한 단순 나열로 추천을 하여 개인화된 추천이 되지 않음  
> ⇒ 사람들은 각자 입맛이 다르고 갖고 있는 재료가 다르므로 개인화된 레시피 추천 서비스의 필요성을 느낌


## 문제 정의

1. 재료 취향 개인화 솔루션
    1. 사용자가 갖고 있는 재료와 재료가 많이 겹치는 레시피를 추천해야 함
    2. 사용자가 좋아하는 레시피의 재료가 유사한 레시피를 추천해야 함
2. 입맛 개인화 솔루션
    1. 사용자와 유사한 사용자들이 좋아하는 레시피를 추천해야 함
    2. 사용자가 좋아하는 레시피의 카테고리에 속하는 레시피를 추천해야 함

# 팀원 소개

| ![image](https://github.com/boostcampaitech5/level2_dkt-recsys-10/assets/60868825/9a929688-e9fa-4d0e-96af-a6c838f9f221) | ![image](https://github.com/boostcampaitech5/level2_dkt-recsys-10/assets/60868825/249da5de-3440-4535-978a-ee898034c7da) | ![image](https://github.com/boostcampaitech5/level2_dkt-recsys-10/assets/60868825/376a2e80-619d-4e5d-ae74-5425e10896b3) | ![image](https://github.com/boostcampaitech5/level2_dkt-recsys-10/assets/60868825/17048a46-9566-430e-b7d8-2d3852cbf99d) | ![image](https://github.com/boostcampaitech5/level2_dkt-recsys-10/assets/60868825/c4e5ed48-8fda-47a1-9fcf-a37f37ac4198) |
| :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: |
|             [김동현](https://github.com/llsy159)             |          [백현주](https://github.com/alexandra9975)          |           [장형규](https://github.com/BrotherGyu)            |            [채민지](https://github.com/chaemj97)             |        [황선우](https://github.com/Vintage-lavender)         |
| # Modeling / EDA<br /> \# UltraGCN, CBF<br />\# 데이터 수집  |       \# Back-end<br />\# 데이터 수집<br />\# Database       | \# Front-end<br />\# Modeling / EDA<br />\# Kobert, Catboost<br />\# Database | \# Modeling / EDA<br />\# TF-IDF, CBF<br />\# 데이터 수집<br />\# 프로젝트 관리 |   \# Modeling / EDA<br />\# BM25, CBF<br />\# 데이터 수집    |

# 프로젝트 상세

## Time Line

![image](/README_files/img/04_TimeLine.png)



## 프로젝트 요구사항 관리

![image](/README_files/img/05_프로젝트요구사항.png)



## Architecture

![image](/README_files/img/06_Architecture.png)

## User Flow
![image](/README_files/img/07_UserFlow.png)

## Model

| Model                      | link                                                         |
| -------------------------- | ------------------------------------------------------------ |
| kobert_rec                 | https://github.com/boostcampaitech5/level3_recsys_finalproject-recsys-10/tree/main/Model/kobert_rec |
| catboost_recipe_classifier | https://github.com/boostcampaitech5/level3_recsys_finalproject-recsys-10/tree/main/Model/catboost_recipe_classifier |
| TF-IDF                     | https://github.com/boostcampaitech5/level3_recsys_finalproject-recsys-10/tree/main/Model/TF-IDF |
| jaccard / bm25             | https://github.com/boostcampaitech5/level3_recsys_finalproject-recsys-10/tree/main/Model/similarity |
| Ingredient_Based_RecSys    | https://github.com/boostcampaitech5/level3_recsys_finalproject-recsys-10/tree/main/Model/Ingredient_Based_RecSys |
| UltraGCN                   | https://github.com/boostcampaitech5/level3_recsys_finalproject-recsys-10/tree/main/Model/UltraGCN |



## Model Result

| ![image](/README_files/img/08_modelresult_1.png) | ![image](/README_files/img/08_modelresult_2.png) |
| ------------------------------------------------------------ | ------------------------------------------------------------ |



## DB Diagram

![image](/README_files/img/09_dbdiagram.png)



# 회고

## 기대효과 및 확장성

### \- 기대효과

- 재료를 기반으로 추천
  - 이외에도 사용자의 선호 레시피를 사용하여 다른 유저와 비교하여 개인화된 추천을 제공  
  - Cold Start를 CBF모델들로 해결 + 사용자의 선호에 따라 추가적인 추천
  
- 상황 고려 추천
  - 사용자가 현재 할 수 있는 레시피들을 추천  
  - 유저 선호 데이터만을 사용하는 것이 아니라, 추가적으로 냉장고 안의 재료와 같은 상황도 고려하여 추천 시스템을 구성

- 자연어 기반 추천, 실시간 개인화 추천으로 기존 플랫폼의 한계 극복
  - 채팅을 사용하여 자신이 어떤 음식을 먹고 싶을 때 드는 생각으로 추천을 제공  
  - 기존의 조회수 기반, 평점기반 추천으로는 개인화 추천이 불가능 했지만, 유저의 선호 데이터를 실시간으로 수집 후 개인화 추천


### \- 확장성

- 확장성: 식재료 홍보 가능
  - 사용자가 가진 재료와 많이 겹치는 레시피를 추천하여 사용자가 레시피의 다른 재료를 구매하게 유도 가능  
  - 식재료 유통사와 협업하여 특정 재료가 들어간 레시피를 추천하는 방식으로 상품 마케팅 가능



## 한계점 및 개선점

- 사용자를 그룹화해서 진행하지 못한 것이 아쉬움
- A/B 테스트 미구현
  - 유저의 선호 상호작용은 실시간으로 가능하지만, 클릭 로그를 수집하는 것은 구현하지 않아 테스트가 어려움
- 오래 걸리는 모델을 사용하기 위한 시스템 구성이 필요
