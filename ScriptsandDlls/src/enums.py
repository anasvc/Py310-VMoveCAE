from enum import Enum
import wx


class FILE_MENU_IDS(Enum):
    # menubar_ids
    LOAD_MODEL = wx.NewIdRef()
    APPEND_RESULT = wx.NewIdRef()
    SAVE_CAX = wx.NewIdRef()
    SAVE_CONFIG_ITEM = wx.NewIdRef()
    FEATURES = wx.NewIdRef()
    INSTANCES = wx.NewIdRef()
    BASIC = wx.NewIdRef()
    ADVANCED = wx.NewIdRef()
    PREFERENCES = wx.NewIdRef()
    HELP = wx.NewIdRef()

    # toolbar ids
    TOOLBAR_LOAD_MODEL = wx.NewIdRef()
    TOOLBAR_APPEND_RESULT = wx.NewIdRef()
    TOOLBAR_SAVE_CAX = wx.NewIdRef()
    CUT_SECTION = wx.NewIdRef()
    ISO_SURFACE = wx.NewIdRef()
    FLOW_LINES = wx.NewIdRef()
    CREATE_RESULT = wx.NewIdRef()
    ATTRIBUTES = wx.NewIdRef()
    RESULT_PROPERTIES = wx.NewIdRef()
    SELECT_MULTIPLE = wx.NewIdRef()
    CHECK_MULTIPLE = wx.NewIdRef()


class ControlItems:
    GEOMETRY = "Geometry"
    RESULTS = "Results"
    INSTANCES = "Instances"
    ALL =  "All"
    INVERT = "Invert"
    CHECKED = "Checked"
    UNCHECKED = "Unchecked"
    SELECTED = "Selected"
    DESELECTED = "Deselected"


class WildCards(Enum):
    ALL_SUPPORTED_FILES = "All Supported Files |*.*"
    ABAQUS_INPUT_FILES = "Abaqus Input files (*.inp)|*.inp"
    NASTRAN_BULK_DATA = "Nastran Bulk Data (*.bdf*;*.nas;*.dat)|*.bdf; *.nas; *.dat"
    NASTRAN_OUTPUT_FILES = "Nastran Output Files(*.op2)|*.op2"
    NASTRAN_XDB_FILES = "Nastran XDB Files (*.xdb)|*.xdb"
    NASTRAN_H5_FILES = "Nastran H5 Files (*.h5)|*.h5"
    ANSYS_INPUT_FILES = "ANSYS Input Files (*.ans;*.cdb)|*.ans; *.cdb"
    ANSYS_STRUCTURAL_ANALYSIS_FILES = "ANSYS Structural Analysis Files (*.rst)|*.rst"
    ANSYS_THERMAL_ANALYSIS_FILES = "ANSYS Thermal Analysis Files (*.rth)|*.rth"
    ABAQUS_FIL_FILES = "ABAQUS FIL Files (*.fil)|*.fil"
    ABAQUS_ODB_FILES = "ABAQUS ODB Files (*.odb)|*.odb"
    LS_DYNA_INPUT_FILES = "LS-Dyna Input Files (*.k;*.key;*.dyn)|*.k; *.key; *.dyn"
    LS_DYNA_D3PLOT_FILES = "LS-Dyna d3plot Files (*d3plot;*.ptf)|*d3plot; *.ptf"
    MSC_MARC_POST_FILES = "MSC.MARC Post Files (*.t16;*.t19)|*.t16; *.t19"
    PTC_MECHANICA_DESIGN_STUDY = "PTC/Mechanica Design Study (*.neu;*.rpt)|*.neu; *.rpt"
    ENSIGHT_GOLD_FILES = "Ensight Gold Files (*.case;*encas)|*.case; *encas"
    FLUENT_MESH_CASE_FILES = "Fluent Mesh/Case Files (*.msh;*.cas)|*.msh; *.cas"
    STARCCM_SOLUTION_FILES = "StarCCM Solution Files (*.ccm;*.ccmt;*.ccmp;*.ccmg)|*.ccm;*.ccmt;*.ccmp;*.ccmg"
    CGNS_FILES = "CGNS Files (*.cgns)|*.cgns"
    ESI_PAM_CARSH_ERFH5_FILES = "ESI PAM-CRASH ERFH5 Files (*.erth5)|*.erth5"
    HYPERMESH_ASCII_FILES = "Hypermesh ASCII Files (*.hmascii)|*.hmascii"
    PATRAN_NEUTRAL_FILES = "Patran Neutral Files (*.pat;*.out)|*.pat;*.out"
    STEROLITHOGRAPHY_FORMAT_FILE = "Sterolithography Format Files (*.stl)|*.stl"
    OPENFOAM_SIMULATION_FILES = "OpenFOAM Simulation Files (controlDict)|*.controlDict"
    CFX_SOLUTION_FILES = "CFX Solution Files (*.res)|*.res"
    SDFC_UNIVERSAL_FILES = "SDFC Universal Files (*.unv)|*.unv"
    TECPLOT_BINARY_FILES = "Tecplot Binary Files (*.plt)|*.plt"
    TERMAS_POST_FILES = "Termas Post Files (*.post)|*.post"
    ALL_FILES = "All Files (*.*)|*.*"


class Formats(Enum):
    ALL_SUP = None
    ABAQUS_INP = 'abaqus_inp'
    NASTRAN_BDF = 'nastran_bdf'
    NASTRAN_OP2 = 'nastran_op2'
    NASTRAN_XDB = 'nastran_xdb'
    NASTRAN_H5 = 'nastran_h5'
    ANSYS_CDB = 'ansys_cdb'
    ANSYS_RST = 'ansys_rst'
    ANSYS_RTH = 'ansys_rth'
    ABAQUS_FIL = 'abaqus_fil'
    ABAQUS_ODB = 'abaqus_odb'
    DYNA_KEY = 'dyna_key'
    DYNA_D3PLOT = 'dyna_d3plot'
    MARC_POST = 'marc_post'
    PTC_NEU_RPT = None
    CASE = 'ensight_case'
    FLUENT_CAS = 'fluent_cas'
    STAR_CCM = 'siemens_starccm'
    CGNS = 'cgns'
    ERFH5 = None
    HYPER_MESH_ASCII = None
    PATRAN_NEUTRAL = None
    STL = None
    CONTROLDICT = None
    CFX_RES = 'cfx_res'
    SFDC_UNI = None
    TECPLOT = 'tecplot_plt'
    THERMAS_POST = None
    ALL_FILES = None


class CheckBoxes(Enum):
    IGNORE_MID_NODES = "Ignore mid-nodes"
    CACHE_INP_FILES = "Cache input files to temporary files folder"
    NODAL_AVG_LOADS = "Nodal averaged loads"
    UNCHECK_ALL_ELEM_SET = "Uncheck \"All Elements\" set"
    UNCHECK_DUP_SET_INSTANCES = "Uncheck duplicate set instances"
    ODB_FAST_LOAD = "ODB fast Load"
    LOAD_FRAMES_NUMBERED_ZERO = "Load frames numbered zero"
    LOAD_INTERNAL_SETS = "Load internal sets"
    PROMPT_FOR_ABAQUS_INP_FILE = "Prompt for Abaqus input file"
    AUTO_UPGRADE_ABAQUS_ODB_FILE = "Auto upgrade Abaqus ODB file"
    NO_AVG_ACROSS_MAT = "No averaging across materials"
    PROMPT_FOR_ANSYS_INP_COMMAND_FILE = "Prompt for Ansys input commands file"
    EXP_MARC_FEATURES = "Experimental Marc features"
    INSTANCE_RES_FILES = "Instance result files"


class PartGroupingPages(Enum):
    ANSYS_CDB_FILES = "Ansys .cdb files"
    ANSYS_RST_RTH_RFL_FILES = "Ansys .rst, .rth and .rfl files"
    NASTRAN_BDF_DAT_FILES = "Nastran .bdf and .dat files"
    NASTRAN_OP2_FILES = "Nastran .op2 files"
    NASTRAN_XDB_FILES = "Nastran .xdb files"
    NASTRAN_H5_FILES = "Nastran .h5 files"
    ABAQUS_INP_FILES = "Abaqus .inp files"
    ABAQUS_ODB_FILES = "Abaqus .odb files"
    ABAQUS_FIL_FILES = "Abaqus .fil files"
    LSDYNA_K_KEY_FILES = "LS-Dyna .k and .key files"
    LSDYNA_D3PLOT_PLT_FILES = "LS-Dyna d3plot and .plt files"
    MSC_MARC_T16_T19_FILES = "MSC.Marc .t16 and .t19 files"


class FormatLabels(Enum):
    ANSYS_CDB = PartGroupingPages.ANSYS_CDB_FILES.value
    ANSYS_RST = PartGroupingPages.ANSYS_RST_RTH_RFL_FILES.value
    NASTRAN_BDF = PartGroupingPages.NASTRAN_BDF_DAT_FILES.value
    NASTRAN_OP2 = PartGroupingPages.NASTRAN_OP2_FILES.value
    NASTRAN_XDB = PartGroupingPages.NASTRAN_XDB_FILES.value
    NASTRAN_H5 = PartGroupingPages.NASTRAN_H5_FILES.value
    ABAQUS_INP = PartGroupingPages.ABAQUS_INP_FILES.value
    ABAQUS_ODB = PartGroupingPages.ABAQUS_ODB_FILES.value
    ABAQUS_FIL = PartGroupingPages.ABAQUS_FIL_FILES.value
    DYNA_KEY = PartGroupingPages.LSDYNA_K_KEY_FILES.value
    DYNA_D3PLOT = PartGroupingPages.LSDYNA_D3PLOT_PLT_FILES.value
    MARC_POST = PartGroupingPages.MSC_MARC_T16_T19_FILES.value


class PartGroupingOptions(Enum):
    DEFAULT = 'Default'
    PROPERTY_ID = 'Property Id'
    MATERIAL_ID = 'Material Id'
    ELEMENT_SET = 'Element Set'
    FACE_SET = 'Face Set'
    ELEMENT_AND_FACE_SETS = 'Element and Face Sets'
    ELEMENT_TYPE_NUMBER = 'Element Type Number'
    NO_PARTS = 'No Parts'
    ANSA_PARTS = 'Ansa Parts'
    HM_COMPONENTS = 'Hypermesh Components'


class GroupingNames(Enum):
    PROPERTY_ID = ["Properties"]
    MATERIAL_ID = ["Materials"]
    ELEMENT_SET = ["Element Sets"]
    FACE_SET = ["Entity sets"]
    ELEMENT_TYPE_NUMBER = ["Element Types"]
    ELEMENT_AND_FACE_SETS = ["Element sets", "Entity sets"]
    NO_PARTS = ["Mesh"]
