import pydicom
import numpy as np


class Patient:

    def __init__(self, name, id, sex, birth_date, study_date, comments):
        self.name = name
        self.id = id
        self.sex = sex
        self.birth_date = birth_date
        self.study_date = study_date
        self.comments = comments


def save_dicom(image, dicom_path, patient_name, patient_id, patient_sex, patient_birth_date, study_date, comments):
    filename = pydicom.data.get_testdata_files("rtplan.dcm")[0]
    ds = pydicom.dcmread(filename)

    ds.PatientName = patient_name
    ds.PatientID = patient_id
    ds.PatientSex = patient_sex
    ds.PatientBirthDate = patient_birth_date
    ds.StudyDate = study_date
    ds.ImageComments = [comments]

    ds.PixelData = image.tobytes()
    ds.Rows = image.shape[0]
    ds.Columns = image.shape[1]

    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7

    ds.save_as(dicom_path)


def read_dicom(dicom_path):
    ref_ds = pydicom.dcmread(dicom_path)

    # Load dimensions based on the number of rows, columns, and slices (along the Z axis)
    const_pixel_dims = (int(ref_ds.Rows), int(ref_ds.Columns))

    # Load spacing values (in mm)
    # ConstPixelSpacing = (float(RefDs.PixelSpacing[0]), float(RefDs.PixelSpacing[1]), float(RefDs.SliceThickness))

    # The array is sized based on 'ConstPixelDims'
    array_dicom = np.zeros(const_pixel_dims, dtype=ref_ds.pixel_array.dtype)

    # store the raw image data
    array_dicom[:, :] = ref_ds.pixel_array

    return array_dicom, Patient(ref_ds.PatientName, '', '', '', '', '')
