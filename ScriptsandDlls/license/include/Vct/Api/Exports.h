/* ==========================================================================
 *       Filename:  Vct/Api/Exports.h
 *      Copyright:  Visual Collaboration Technologies Inc.
 * ======================================================================== */

/**
 * \file
 * @brief Provides the export related declarations
 */

#ifndef Vct_Api_Exports_h
#define Vct_Api_Exports_h

#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#   pragma once
#endif

#ifdef VCT_NO_API
#   define VCT_API
#else
#   ifdef WIN32
#       ifdef VCT_API_EXPORTS
#           define VCT_API __declspec(dllexport)
#       else
#           define VCT_API __declspec(dllimport)
#       endif
#   else
#       define VCT_API
#   endif
#endif

#endif // Vct_Api_Exports_h
