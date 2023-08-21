/* ==========================================================================
 *       Filename:  Vct/License/SuiteImpl.h
 *      Copyright:  Visual Collaboration Technologies Inc.
 * ======================================================================== */

/**
 * \file
 * @brief Provides the implementation details for Suite Class
 *
 */

#ifndef Vct_License_SuiteImpl_h
#define Vct_License_SuiteImpl_h

#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#   pragma once
#endif

#ifndef __cplusplus
#   error This is a C++ include file and cannot be used from plain C
#endif

#include <string>
#include <map>
#include "Vct/License/Suite.h"
#include "lmpolicy.h"
#include "lmclient.h"
#include "lm_attr.h"

namespace Vct {
namespace License {

    /**
     */
    class Suite::Impl {
    public:     // types
        ///
        struct FeatureInfo
        {
            std::string m_sVendorString;    //VendorString used for this feature
            int m_iTotalLicensesIssued;        //max num of lic avail in this vd-pool for this feature
            int m_iTotalLicensesInUse;        //Total no. of licenses in use (Reserved and non-reserved licenses)
            int m_iLicensesInUse;            //Total no. of licenses in use (non-reserved licenses only)
            int m_iReservedLicenses;        //Total no. of licenses reserved
            int m_iTimeOut;                    //Timeout
            std::string m_sStartDate;        //Start date for the feature
            std::string m_sExpiryDate;        //expiry date for the feature
            std::string m_sVendorName;        //Vendor Name used for this feature
            std::string m_sHostId;            //HostId of the license server
            std::string m_sHostName;        //HostName of the license server
            int m_iPortNumber;                //port number used in the license

            bool m_bBorrowed;                //
            int m_iNoOfDaysAvailable;
        };

        ///
        typedef std::map<std::string, FeatureInfo*> FeatureInfoMap;

    public:     // structors
        /**
         */
        Impl() {
			lm_job = NULL;
        }

        /**
         */
        virtual ~Impl() {
        }

    public:     // methods
        /**
         */
        bool GetFeatureInfo(const char *sFeature, const char *sVersion) {

			const size_t MAX_STR_LEN = 1024;

			char feature[MAX_STR_LEN+1];
			char version[MAX_STR_LEN+1];
			char licDir[MAX_STR_LEN+1];

			feature[MAX_STR_LEN] = '\0';
			version[MAX_STR_LEN] = '\0';
			licDir[MAX_STR_LEN] = '\0';

			strncpy(feature, sFeature, MAX_STR_LEN);
			strncpy(version, sVersion, MAX_STR_LEN);

			GetWindowsDirectory(licDir,MAX_STR_LEN);

			LM_HANDLE *test_lm_job;
			VENDORCODE code;
			if (lc_new_job(0, lc_new_job_arg2, &code, &test_lm_job))
			{
				lc_perror(test_lm_job, "lc_new_job failed");
				exit(lc_get_errno(test_lm_job));
			}

			/*
				* To suppress the FLEXnet License Finder dialog*
				*/
			lc_set_attr(test_lm_job, LM_A_PROMPT_FOR_FILE, (LM_A_VAL_TYPE)0);

			/*
				* To specify the default License File path
				*/
			lc_set_attr(test_lm_job, LM_A_LICENSE_DEFAULT, (LM_A_VAL_TYPE)licDir);

			/*
				* To check the back-date
				*/
			lc_set_attr(test_lm_job, LM_CHECK_BADDATE, (LM_A_VAL_TYPE)1);

			if (lc_checkout(test_lm_job, (LPSTR) sFeature, version, 1, 
								LM_CO_LOCALTEST, &code, LM_DUP_NONE
								)
				)
			{ 
				lc_free_job(test_lm_job);
				return false;//lc_get_errno(test_lm_job);
			}
			else
			{
				CONFIG *conf = lc_test_conf(test_lm_job);
				if(!conf)
					return false;

				FeatureInfo *pFeatureInfo = NULL;
				std::map<std::string,FeatureInfo*>::iterator it; 
				it = m_FeatureInfoMap.find(std::string(sFeature));
				if (it != m_FeatureInfoMap.end())
				{
					//The features information is already extracted and filled in the structure. So no need to get the values again.
					pFeatureInfo = it->second;
					if(!pFeatureInfo)
						return false;

					return true;
				}
				else
				{
					pFeatureInfo = new FeatureInfo;
					pFeatureInfo->m_sVendorString = "";
					pFeatureInfo->m_iTotalLicensesIssued = -1;
					pFeatureInfo->m_iTotalLicensesInUse = -1;
					pFeatureInfo->m_iLicensesInUse = -1;		
					pFeatureInfo->m_iReservedLicenses = -1;	
					pFeatureInfo->m_iTimeOut = -1;				
					pFeatureInfo->m_sStartDate = "";		
					pFeatureInfo->m_sExpiryDate = "";		
					pFeatureInfo->m_sVendorName = "";		
					pFeatureInfo->m_sHostId = "";			
					pFeatureInfo->m_sHostName = "";		
					pFeatureInfo->m_iPortNumber = -1;	
					pFeatureInfo->m_bBorrowed = false;

					m_FeatureInfoMap[sFeature] = pFeatureInfo;
				}
				if(conf)
				{
					pFeatureInfo->m_iNoOfDaysAvailable = lc_expire_days(test_lm_job, conf);

					//Vendor String
					if(conf->lc_vendor_def && strlen(conf->lc_vendor_def))
						pFeatureInfo->m_sVendorString = conf->lc_vendor_def;

					//License Start Date
					if(conf->startdate && strlen(conf->startdate))
						pFeatureInfo->m_sStartDate = (conf->startdate);

					//License Expiry Date
					if(conf->date && strlen(conf->date))
						pFeatureInfo->m_sExpiryDate = (conf->date);

					//Hostname of License Server
					if(conf->server && conf->server->name && strlen(conf->server->name))
						pFeatureInfo->m_sHostName = (conf->server->name);

					//Port number
					if(conf->server)
						pFeatureInfo->m_iPortNumber =  conf->server->port;

					//Borrow Flag
					if(conf->borrow_flags==1)
						pFeatureInfo->m_bBorrowed = true;

					//int lc_max_borrow_hours = conf->lc_max_borrow_hours;

					LM_BORROW_STAT bs;
					lc_get_attr(test_lm_job,LM_A_BORROW_STAT,(short *)&bs);


					LM_VD_FEATURE_INFO fi;
					fi.feat = conf;
					if(!lc_get_attr(test_lm_job, LM_A_VD_FEATURE_INFO, (short *)&fi))
					{
						pFeatureInfo->m_iTimeOut = fi.timeout;
						pFeatureInfo->m_iTotalLicensesIssued = fi.num_lic;		
						pFeatureInfo->m_iTotalLicensesInUse = fi.tot_lic_in_use;
						pFeatureInfo->m_iLicensesInUse = fi.float_in_use;
						pFeatureInfo->m_iReservedLicenses = fi.res;
					}



				}
				lc_free_job(test_lm_job);
			}
			return true;

        }

        /**
         */
        FeatureInfo* GetFeature(const char* sFeature,const char* sVersion) 
		{
			FeatureInfo* pFeatureInfo = NULL;
			std::map<std::string,FeatureInfo*>::iterator it; 
			it = m_FeatureInfoMap.find(std::string(sFeature));
			if (it != m_FeatureInfoMap.end())
			{
				//The features information is already extracted and filled in the structure. So no need to get the values again.
				pFeatureInfo = it->second;
			}
			if(!pFeatureInfo)
			{
				if(GetFeatureInfo(sFeature,sVersion))
				{
					it = m_FeatureInfoMap.find(std::string(sFeature));
					if (it != m_FeatureInfoMap.end())
					{
						pFeatureInfo = it->second;
					}
				}
				else
					//throw std::runtime_error("No such feature");
					return NULL;
			}
			return pFeatureInfo;
        }
       
		/// Error code of the last failed call 
        int m_iLastError;
        /// Error string of the last failed call
        char m_sLastErrorString[1024];
		LM_HANDLE *lm_job;
    private:    // attributes


        ///
        FeatureInfoMap m_FeatureInfoMap;


    };

} // namespace License
} // namespace Vct

#endif // Vct_License_SuiteImpl_h
