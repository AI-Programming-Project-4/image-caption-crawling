# image-caption-crawling
Flowchart image &amp; caption crawling for CC BY-NC-SA 4.0 licensed papers

<목표>
1. arXiv 논문 중 (CC BY 4.0 이상의 라이선스를 가진) 논문에서 flowchart 이미지 & 캡션 pair 크롤링
2. 수집한 pair를 유형 분류 (ex: 이미지 포함O, 이미지 포함X)

<방법>
- HuggingFace의 오픈 데이터셋 ArxivCap을 활용 (Dataset Summary: The ArxivCap dataset consists of 6.4 million images and 3.9 million captions with 193 million words from 570k academic papers accompanied with abstracts and titles. (papers before June 2023))
- 1st step: Hugging Face의 Hugging Face 에 공개된 ArxivCap 데이터셋을 활용하여, 컴퓨터 비전·머신러닝·AI·멀티모달 분야 논문(cs.CV, cs.LG, cs.AI 등)의 figure 중 architecture, framework, pipeline, workflow 등의 키워드를 포함한 이미지–캡션 pair를 자동 필터링 및 수집.
- 2nd step: image viewer를 활용하여 실제로 flowchart이미지인 것만을 추가 검수.
- 3rd step: flowchart 이미지를 이미지가 포함된 것과 그렇지 않은 것으로 구분
- 4th step: 너무 복잡한 플로우차트는 학습에 방해되므로 간단한 flowchart만 남기는 방향으로 추가 검수

<결과>
- 1st step에서 8000개 수집 후, 2nd step에서 3000개 검수하여 259개의 flow chart image 및 캡션 수집 완료. (디렉토리: images_flowcharts)
- 259개의 이미지를 이미지가 포함된 플로우 차트 42개, 이미지가 포함되지 않은 플로우 차트 217개로 분류 완료. (디렉토리: images_flowcharts_exclude_image, images_flowcharts_include_image)
- 복잡한 플로우차트 이미지를 제거하여 최종적으로 이미지가 포함된 플로우 차트 36개, 이미지가 포함되지 않은 플로우 차트 196개로 분류 완료. (디렉토리: images_flowcharts_exclude_image_final, images_flowcharts_include_image_final)

<복잡한 플로우차트 이미지 제거 기준>
- 전형적인 플로우차트 이미지(주로 도형과 화살표로 이루어져 일정한 흐름이 있는 플로우차트)만 유지
- depth가 10 이상인 플로우차트 제거

<복잡하여 제거된 플로우차트 예시>
A. 전형적인 플로우차트 이미지가 아닌 것
<img width="2016" height="1185" alt="001188" src="https://github.com/user-attachments/assets/85ef5535-eb4e-41d4-89e8-4cb884e5da55" />
<img width="2016" height="1427" alt="001297" src="https://github.com/user-attachments/assets/744f2bed-4d9e-4be9-8cbe-e573f6bff6c0" />

B. 전형적인 플로우차트 이미지이지만 depth가 10이상인 것
<img width="1345" height="2016" alt="000786" src="https://github.com/user-attachments/assets/b66f32da-909a-48c2-b11c-f178c3cb6c1a" />
<img width="2016" height="1433" alt="000771" src="https://github.com/user-attachments/assets/56a6d8ec-4546-4634-beb8-a8ce700c0e6e" />

