<div id="top"></div>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/orelts/transformation_gui">
  <img width="300", img height="100 alt="app" src="https://user-images.githubusercontent.com/59450815/173082914-536dd91b-1077-41bd-bc07-d5781330010f.png">
  </a>

  <h3 align="center">Transformation Gui</h3>

  <p align="center">
    An interactive way to apply multiple linear 3x3 transformation on 2D Polygons
    <br />
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project serves as GUI for visualization of matrix linear transformation on Polygons. The user can choose Polygons corners at start 
of the application and then apply all sort of 3x3 transformations. The result will show immediately.

<p align="right">(<a href="#top">back to top</a>)</p>

### Built With


* [Python](https://python.org/)
* [Tkinter](https://docs.python.org/3/library/tkinter.html)
                            
<p align="right">(<a href="#top">back to top</a>)</p>


<!-- GETTING STARTED -->
                                
## Getting Started
This tutorial is for creating executable file. The other possibility is to clone the project and run the trans_gui.py.                                 
                         
                                
### Prerequisites

* Clone the project                                
  ```sh
  git clone https://github.com/orelts/transformation_gui.git
  ```
* Install pyinstaller                               
  ```sh
  pip install pyinstaller
  ```     

### Installation
                                
1. Create executable file from the trans_gui.py script
   ```sh
   pyinstaller.exe --onefile -w  .\trans_gui.py
   ```
After it will finish the .exe file will be ready under dist folder

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage
At first 2 canvas will show, one for the application and one for the polygon creation. 
Open the Polygon selection window. Make sure not to close the application window
                                
<br />
<div align="center">
  <img width="500", img height="200" alt="app" src="https://user-images.githubusercontent.com/59450815/173087121-45aafe50-82cb-47c8-86f0-36e3095d27a6.png">
  </a>

  <p align="center">
    Click for Polygon corners selection.
    <br />
  </p>
</div>                                

<br />
<div align="center">
  <img width="500", img height="200", alt="after_selection" src="https://user-images.githubusercontent.com/59450815/173088417-78a78cc8-453a-4c53-ac23-17d3c1333036.png">

  </a>

  <p align="center">
    Now matrix transformation can be applied by the submit button
    <br />
  </p>
</div> 
                   
<br />
<div align="center">
<img width="500", img height="200", alt="transformed" src="https://user-images.githubusercontent.com/59450815/173089986-ab70b8bb-e9cb-4d0d-84ed-678cd6e89199.png">
           
  </a>
  <p align="center">
    This is example for 90 degrees rotation
    <br />
  </p>
</div>                   

<p align="right">(<a href="#top">back to top</a>)</p>






<!-- CONTRIBUTING -->
## Contributing

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- CONTACT -->
## Contact

Orel Tsioni - oreltsioni@gmail.com

Project Link: [https://github.com/orelts/transformation_gui](https://github.com/orelts/transformation_gui)

<p align="right">(<a href="#top">back to top</a>)</p>






