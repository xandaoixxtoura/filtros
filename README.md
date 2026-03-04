# Filtros Analógicos Interativos

Um projetinho em Python para desenhar e analisar filtros analógicos de forma visual, usando uma interface gráfica simples.

## O que esse projeto faz

- Calcula protótipos Butterworth e Chebyshev a partir de especificações em dB e Hz.
- Gera filtros passa-baixa, passa-alta e passa-faixa.
- Decompõe o filtro em estágios de 2ª ordem (Sallen-Key e MFB).
- Mostra equações, parâmetros de cada estágio e o circuito equivalente.

A ideia é ter uma ferramenta de apoio para disciplina de filtros, onde dá para ajustar os requisitos e ver o resultado na hora.

## Tecnologias

- Python 3
- Tkinter para a interface gráfica
- control, scipy e sympy para o lado matemático
- schemdraw para os diagramas de circuito

## Como rodar

1. Clonar o repositório:

   git clone https://github.com/xandaoixxtoura/filtros.git
   cd filtros

2. Criar e ativar o ambiente virtual (opcional, mas recomendado):

   python -m venv .venv
   .venv\Scripts\activate   # Windows

3. Instalar as dependências:

   pip install -r requirements.txt

4. Rodar a aplicação:

   python main.py

## Uso básico

- Escolha o tipo de filtro (PB, PA, PF).
- Informe Amin, Amax, Ws e Wp.
- Selecione a topologia desejada (Sallen-Key ou MFB).
- Clique em calcular e veja os estágios com seus componentes.

## Status do projeto

Projeto em desenvolvimento, focado em estudos de filtros analógicos na graduação.  
Sugestões de melhoria são bem-vindas via issues ou pull requests.


