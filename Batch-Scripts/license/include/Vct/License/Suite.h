/* ==========================================================================
 *       Filename:  Vct/License/Suite.h
 *      Copyright:  Visual Collaboration Technologies Inc.
 * ======================================================================== */

/**
 * \file
 * @brief Provides the interface to VCollab Suite license checkouts and checkins
 *
 */

#ifndef Vct_License_Suite_h
#define Vct_License_Suite_h

#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#   pragma once
#endif

#ifndef __cplusplus
#   error This is a C++ include file and cannot be used from plain C
#endif

#include "Vct/Api/Exports.h"

namespace Vct {
namespace License {

    /**
     */
    class VCT_API Suite {
    public:     // types
        ///
        class Impl;

    public:     // structors
        /**
         */
        Suite();

        /**
         */
        virtual ~Suite();

    public:     // methods
        /**
         * Acquire License:
                iShowMessage  options : NoMessage = 0, ShowMessage = 1 
                iCheckOutFlag options : LM_CO_NOWAIT=0, LM_CO_WAIT=1 ,LM_CO_QUEUE=2
         */
        bool CheckOut(const char *sFeature, const char *sVal, int iShowMessage=0, int iCheckOutFlag=0);

        /**
         * Release License
         */
        void CheckIn(const char *sFeature);

        /**
         */
        bool CheckHeart();

        /**
         */
        int GetLastError() const;

        /**
         */
        const char* GetErrorString() const;

        /**
         * Get the number of available days for the requested feature
		 *
		 * Return Value:  1 - Success , 0 - Failure
         */
        int GetAvailableDays(const char *sFeature, const char *sVersion, int &iNoOfDaysAvailable, char *sAvailabilityMsg = "NULL");

        /*
         * Get the Start date and expiry date fro the requested feature
		 * 
		 * Return Value:  True - Success , False - Failure
         */
        bool GetDates(const char * sFeature, const char * sVersion,char *sStartDate, char *sExpiryDate);


        /*
         * Get the VENDOR_STRING for the requested feature
         */
        const char* GetVendorString(const char* sFeature,const char* sVersion) const;

        /*
         * Get the following licenses count for the requested feature
         *
         * iTotalLicensesIssued        :    Total No. of licenses issued to customer
         * iTotalLicensesReserved    :    Total No. of licenses reserved by the customer
         * iTotalLicensesInUse        :    Total No. of licenses are already used (Reserved and non-reserved licenses)
         * iLicensesInUse            :    Total No. of licenses are already used (Non-reserved licenses)
         *
		 * Return Value:  True - Success , False - Failure
        */
        bool GetLicensesCount(const char * sFeature, const char * sVersion, int &iTotalLicensesIssued, int &iTotalLicensesReserved, int &iTotalLicensesInUse, int &iLicensesInUse);

        /*
         * Get the TIMEOUT time set by the customer for the requested feature
        */
        int GetTimeOutValue(const char * sFeature, const char * sVersion);

    protected:      // attributes
        ///
        Impl * mpImpl;
    };

} // namespace License
} // namespace Vct

#endif // Vct_License_Suite_h
