# image-caption-crawling
Flowchart image &amp; caption crawling for CC BY-NC-SA 4.0 licensed papers

<목표>
1. arXiv 논문 중 (CC BY 4.0 이상의 라이선스를 가진) 논문에서 flowchart 이미지 & 캡션 pair 크롤링
2. 수집한 pair를 유형 분류 (ex: 모델, 흐름도)

<방법>
- HuggingFace의 오픈 데이터셋 ArxivCap을 활용 (Dataset Summary: The ArxivCap dataset consists of 6.4 million images and 3.9 million captions with 193 million words from 570k academic papers accompanied with abstracts and titles. (papers before June 2023))
- 1st step: Hugging Face의 Hugging Face 에 공개된 ArxivCap 데이터셋을 활용하여, 컴퓨터 비전·머신러닝·AI·멀티모달 분야 논문(cs.CV, cs.LG, cs.AI 등)의 figure 중 architecture, framework, pipeline, workflow 등의 키워드를 포함한 이미지–캡션 pair를 자동 필터링 및 수집.
- 2nd step: image viewer를 활용하여 실제로 flowchart이미지인 것만을 추가 검수.

<결과>
- 1st step에서 8000개 수집 후, 2nd step에서 2000개 검수하여 191개의 flow chart image 및 캡션 수집 완료.
