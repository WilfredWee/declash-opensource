# DeClash
#### Note: This project is currently inactive. If you are interested to work on this, feel free to fork it or even better, get in touch with me and see if we can work something out.

## Introduction
This software was initially built in early 2014 to serve the needs of the University of British Columbia Debating Society, where during peak season (at the start of the school term), there are many debaters and no efficient conduct debate practice.

This software aims to solve that by registering debaters/judges, and assign them partners, rooms and roles accordingly.

This software has been tested with British Parliamentary, but theoretically works with Asian Parliamentary and Canadian Parliamentary as well. (Theoretically is a stretch, bugs are a given.)


## Codebase Introduction
DeClash is built on Django 1.7 and Angular 1.0.

Django serves as (almost) strictly a REST API service for Angular to consume. Built on Django REST Framework.

Angular serves as an autonamous unit for the front-end that treats the implementation of the API as a black box. Therefore you'll see duplication of logic checks etc. This is by design.

All front-end code do not have a build system in place and third-party libraries are manually checked-in.

Additionally, the project has the skeleton in place for integration with AWS Elastic Beanstalk.

## License
The MIT License (MIT)

Copyright (c) 2014-2015 Wilfred Wee

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
