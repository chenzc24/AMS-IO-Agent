#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Device Type Classification Module
"""

class DeviceClassifier:
    """Device Type Classifier"""
    
    @staticmethod
    def is_digital_device(device_type: str) -> bool:
        """Check if it's a digital device"""
        digital_devices = [
            "PDDW16SDGZ_V_G", "PDDW16SDGZ_H_G",
            "PVDD1DGZ_V_G", "PVDD1DGZ_H_G",
            "PVSS1DGZ_V_G", "PVSS1DGZ_H_G",
            "PVDD2POC_V_G", "PVDD2POC_H_G",
            "PVSS2DGZ_V_G", "PVSS2DGZ_H_G"
        ]
        return device_type in digital_devices
    
    @staticmethod
    def is_analog_device(device_type: str) -> bool:
        """Check if it's an analog device"""
        analog_devices = [
            "PDB3AC_V_G", "PDB3AC_H_G",
            "PVDD1AC_V_G", "PVDD1AC_H_G",
            "PVSS1AC_V_G", "PVSS1AC_H_G",
            "PVDD3A_V_G", "PVDD3A_H_G",
            "PVSS3A_V_G", "PVSS3A_H_G",
            "PVDD3AC_V_G", "PVDD3AC_H_G",
            "PVSS3AC_V_G", "PVSS3AC_H_G"
        ]
        return device_type in analog_devices
    
    @staticmethod
    def is_digital_io_device(device_type: str) -> bool:
        """Check if it's a digital IO device"""
        digital_io_devices = ["PDDW16SDGZ_V_G", "PDDW16SDGZ_H_G"]
        return device_type in digital_io_devices
    
    @staticmethod
    def is_corner_device(device_type: str) -> bool:
        """Check if it's a corner component"""
        corner_devices = ["PCORNERA_G", "PCORNER_G"]
        return device_type in corner_devices
    
    @staticmethod
    def is_filler_device(device_type: str) -> bool:
        """Check if it's a filler component"""
        filler_devices = ["PFILLER10A_G", "PFILLER20A_G", "PFILLER10_G", "PFILLER20_G"]
        return device_type in filler_devices
    
    @staticmethod
    def is_separator_device(device_type: str) -> bool:
        """Check if it's a separator component"""
        separator_devices = ["PRCUTA_G"]
        return device_type in separator_devices 