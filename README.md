# Personal Flask Website with ISS Viewing Guide

A Flask-based personal website hosted on Raspberry Pi 2, featuring web applications including an ISS (International Space Station) Viewing Guide.

## Project Overview
This website serves as a platform for hosting various web applications. Currently featuring:
- ISS Viewing Guide: Get real-time ISS position and upcoming viewing passes for any location

## Technical Details

### Hardware
- Raspberry Pi 2
- Operating System: Raspberry Pi OS (32-bit)

### Backend
- Python 3.11
- Flask web framework
- Virtual Environment for dependency management

### Frontend
- Bootstrap 5.3 for responsive design
- Dark theme with custom CSS styling
- Mobile-friendly interface

### APIs Used
- N2YO API for ISS tracking
- Nominatim for geocoding services

## Dependencies
- Flask
- Requests
- Pytz
- TimezoneFinder
- Geopy
- Python-dotenv
