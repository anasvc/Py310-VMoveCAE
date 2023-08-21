/*
 * ===========================================================================
 *
 *       Filename:  VCollabSuiteLicense.h
 *
 *    Description:
 *
 * FLEXlm Version:  11.11.0.0
 *  Build Version:  2.0
 *        Created:  4/19/2013 17:00
 *       Revision:  none
 *       Compiler:  vc8, gcc, icpc
 *         Author:
 *        Company:  Visual Collaboration Technologies Inc.
 *
 *
 * ===========================================================================
 */

#ifndef Vct_VCollabSuiteLisense_h
#define Vct_VCollabSuiteLisense_h

#ifndef __cplusplus
#error This is a C++ include file and cannot be used from plain C
#endif

#if defined(_MSC_VER)
    #if _MSC_VER > 1000
        #pragma once
    #endif // _MSC_VER > 1000

    // Exclude rarely-used stuff from Windows headers
    #define WIN32_LEAN_AND_MEAN
    #include <windows.h>
#endif
#include <string>
#include <map>

#if defined(_MSC_VER)
    // The following ifdef block is the standard way of creating macros 
    // which make exporting from a Windows DLL simpler. All files within this 
    // DLL are compiled with the VCOLLABSUITELICENSE_EXPORTS symbol defined 
    // on the command line. This symbol should not be defined on any project 
    // that uses this DLL. This way any other project whose source files 
    // include this file see VCOLLABSUITELICENSE_API functions as being 
    // imported from a DLL, wheras this DLL sees symbols defined with this 
    // macro as being exported.
    #ifdef VCOLLABSUITELICENSE_EXPORTS
        #define VCOLLABSUITELICENSE_API __declspec(dllexport)
    #else
        #define VCOLLABSUITELICENSE_API __declspec(dllimport)
    #endif
#else
    #define VCOLLABSUITELICENSE_API
#endif

namespace Vct {

    /**
     * VCollab License management class
     */
    class VCOLLABSUITELICENSE_API CVCollabSuiteLicense 
    {
    public:     // structors
        /**
         * Constructor
         */
        CVCollabSuiteLicense(void);

    public:     // methods

        /**
         * Acquire License:
		            iShowMessage  options : NoMessage = 0, ShowMessage = 1 
		            iCheckOutFlag options : LM_CO_NOWAIT=0, LM_CO_WAIT=1 ,LM_CO_QUEUE=2
         */
        bool CheckOut(const char *sFeature, const char *sVal="NULL",int iShowMessage=0,
			                                                        int iCheckOutFlag=0 
                                                    );

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
		 *
		 * Feature Information for the requested license feature
		 *
		*/
			/**
			 * Get the number of available days for the requested feature
			 */
			int  GetAvailableDays(const char *sFeature,const char *sVersion,int &iNoOfDaysAvailable,char *sAvailabilityMsg="NULL");

			/*
			 * Get the Start date and expiry date fro the requested feature
			*/
			bool GetDates(std::string sFeature, std::string sVersion,std::string &sStartDate, std::string &sExpiryDate);

			/*
			 * Get the status if the license is borrowed for the requested feature
			*/
			//bool GetBorrowedInfo(std::string sFeature, std::string sVersion, bool &bBorrowed);

			/*
			 * Get the VENDOR_STRING for the requested feature
			*/
			bool GetVendorString(std::string sFeature, std::string sVersion,std::string &sVendorString);

			/*
			 * Get the following licenses count for the requested feature
			 *
			 * iTotalLicensesIssued		:	Total No. of licenses issued to customer
			 * iTotalLicensesReserved	:	Total No. of licenses reserved by the customer
			 * iTotalLicensesInUse		:	Total No. of licenses are already used (Reserved and non-reserved licenses)
			 * iLicensesInUse			:	Total No. of licenses are already used (Non-reserved licenses)
			 *
			*/
			bool GetLicensesCount(std::string sFeature, std::string sVersion, int &iTotalLicensesIssued, int &iTotalLicensesReserved, int &iTotalLicensesInUse, int &iLicensesInUse);

			/*
			 * Get the TIMEOUT time set by the customer for the requested feature
			*/
			bool GetTimeOutValue(std::string sFeature, std::string sVersion, int &iTimeOut);



	private:       // attributes

        /// Error code of the last failed call 
        int m_iLastError;

		struct FeatureInfo{
			std::string m_sVendorString;	//VendorString used for this feature
			int m_iTotalLicensesIssued;		//max num of lic avail in this vd-pool for this feature
			int m_iTotalLicensesInUse;		//Total no. of licenses in use (Reserved and non-reserved licenses)
			int m_iLicensesInUse;			//Total no. of licenses in use (non-reserved licenses only)
			int m_iReservedLicenses;		//Total no. of licenses reserved
			int m_iTimeOut;					//Timeout
			std::string m_sStartDate;		//Start date for the feature
			std::string m_sExpiryDate;		//expiry date for the feature
			std::string m_sVendorName;		//Vendor Name used for this feature
			std::string m_sHostId;			//HostId of the license server
			std::string m_sHostName;		//HostName of the license server
			int m_iPortNumber;				//port number used in the license

			bool m_bBorrowed;				//
			int m_iNoOfDaysAvailable;
		};

#pragma warning(push)
#pragma warning(disable:4251)
		std::map<std::string,FeatureInfo*> m_FeatureInfoMap;
#pragma warning(pop)

		FeatureInfo* GetFeature(std::string sFeature, std::string sVersion);
		bool GetFeatureInfo(const char *sFeature,const char *sVersion);

#pragma warning(push)
#pragma warning(disable:4251)
        /// Error string of the last failed call
        char m_sLastErrorString[1024];
#pragma warning(pop)

    };      // class CVCollabSuiteLicense

}   // namespace Vct

#endif     // Vct_VCollabSuiteLisense_h


