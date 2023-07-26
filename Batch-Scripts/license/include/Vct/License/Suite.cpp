/* ==========================================================================
 *       Filename:  Vct/License/Suite.cpp
 *      Copyright:  Visual Collaboration Technologies Inc.
 * ======================================================================== */

#include <string>
#include "Vct/License/Suite.h"
#include "Vct/License/SuiteImpl.h"

namespace Vct { namespace License {

    Suite::Suite () : mpImpl(new Impl) {
    }

    Suite::~Suite() {
        delete mpImpl;
    }

    bool Suite::CheckOut(const char *sFeature, const char *sVersion, int iShowMessage, int iCheckOutFlag) {
		const size_t MAX_STR_LEN = 1024;
		char feature[MAX_STR_LEN+1];
		char version[MAX_STR_LEN+1];
		char licDir[MAX_STR_LEN+1];

		feature[MAX_STR_LEN] = '\0';
		version[MAX_STR_LEN] = '\0';
		licDir[MAX_STR_LEN] = '\0';

		//::MessageBox(NULL,"2","VCollab License",0);
		strncpy(feature, sFeature, MAX_STR_LEN);
		strncpy(version, sVersion, MAX_STR_LEN);
		//::MessageBox(NULL,"3","VCollab License",0);

#ifdef WIN32
        GetWindowsDirectory(licDir, MAX_STR_LEN);
#else
        strncpy(licDir, "/usr/share/licenses:/usr/local/share/licenses:"
                       "/opt/share/licenses:/opt/licenses", 
                       MAX_STR_LEN);
#endif
		//::MessageBox(NULL,"4","VCollab License",0);

		VENDORCODE code;
		if (lc_new_job(0, lc_new_job_arg2, &code, &mpImpl->lm_job))
		{
			lc_perror(mpImpl->lm_job, "lc_new_job failed");
			exit(lc_get_errno(mpImpl->lm_job));
		}
		//::MessageBox(NULL,"5","VCollab License",0);


		/*
		 * To suppress the FLEXnet License Finder dialog*
		 */
		lc_set_attr(mpImpl->lm_job, LM_A_PROMPT_FOR_FILE, (LM_A_VAL_TYPE)0);
		//::MessageBox(NULL,"6","VCollab License",0);

		/*
		 * To specify the default License File path
		 */
		lc_set_attr(mpImpl->lm_job, LM_A_LICENSE_DEFAULT, (LM_A_VAL_TYPE)licDir);
		//::MessageBox(NULL,"7","VCollab License",0);

		/*
		 * To check the back-date
		 */
		lc_set_attr(mpImpl->lm_job, LM_CHECK_BADDATE, (LM_A_VAL_TYPE)1);
		//::MessageBox(NULL,"8","VCollab License",0);
		//::MessageBox(NULL,"VCollabSuiteLicense : b4 checkout","VCollab License",0);

		//Added 1 line on 3-Jun-2016
		//For enabling TIMEOUT feature
		lc_idle(mpImpl->lm_job,1);

		if (!lc_checkout(mpImpl->lm_job, (LPSTR) sFeature, version, 1, 
						 iCheckOutFlag, &code, LM_DUP_NONE
						 )
		   )
		{
			return true; 
		}
		//::MessageBox(NULL,"VCollabSuiteLicense : after checkout","VCollab License",0);
		//::MessageBox(NULL,"10","VCollab License",0);

		if(iShowMessage)
			lc_perror(mpImpl->lm_job, "checkout failed");

		mpImpl->m_iLastError = lc_get_errno(mpImpl->lm_job);
		strncpy(mpImpl->m_sLastErrorString,lc_errstring(mpImpl->lm_job), MAX_STR_LEN);
		//exit (lc_get_errno(lm_job));
		return false;

    }

    void Suite::CheckIn(const char *sFeature) {
		const size_t MAX_STR_LEN = 1024;
		char feature[MAX_STR_LEN+1];
		feature[MAX_STR_LEN] = '\0';
		strncpy(feature, sFeature, MAX_STR_LEN);

		lc_checkin(mpImpl->lm_job, feature, 0); 
    }

    bool Suite::CheckHeart() {
        return false;
    }

    int Suite::GetLastError() const {
        return mpImpl->m_iLastError;
    }

    const char* Suite::GetErrorString() const {
        return mpImpl->m_sLastErrorString;
    }

    const char* Suite::GetVendorString(const char* sFeature, const char * sVersion) const {
        try {
            Impl::FeatureInfo* feature_info = mpImpl->GetFeature(sFeature,sVersion);
			if(!feature_info)
			{
				return nullptr;
			}
            return feature_info->m_sVendorString.c_str();
        } catch(std::runtime_error&) {
            return nullptr;
        }
    }

	bool Suite::GetDates(const char * sFeature, const char * sVersion,
						 char* StartDate, 
						 char* sExpiryDate)
	{
		Impl::FeatureInfo *pFeatureInfo=mpImpl->GetFeature(sFeature,sVersion);
		if(!pFeatureInfo)
		{
			StartDate = "";
			sExpiryDate = "";
			return false;
		}

		strcpy(StartDate,pFeatureInfo->m_sStartDate.c_str());
		strcpy(sExpiryDate,pFeatureInfo->m_sExpiryDate.c_str());
		return true;
	}

	bool Suite::GetLicensesCount(const char * sFeature, const char * sVersion, 
		                         int &TotalLicensesIssued, int &TotalLicensesReserved, int &iTotalLicensesInUse, int &iLicensesInUse)
	{
		Impl::FeatureInfo *pFeatureInfo=mpImpl->GetFeature(sFeature,sVersion);
		if(!pFeatureInfo)
		{
			TotalLicensesIssued = -1;
			TotalLicensesReserved = -1;
			iTotalLicensesInUse = -1;
			iLicensesInUse = -1;
			return false;
		}
		TotalLicensesIssued = pFeatureInfo->m_iTotalLicensesIssued;
		TotalLicensesReserved = pFeatureInfo->m_iReservedLicenses;
		iTotalLicensesInUse = pFeatureInfo->m_iTotalLicensesInUse;
		iLicensesInUse = pFeatureInfo->m_iLicensesInUse;
		return true;
	}
	int Suite::GetTimeOutValue(const char * sFeature, const char * sVersion)
	{
		Impl::FeatureInfo *pFeatureInfo=mpImpl->GetFeature(sFeature,sVersion);
		if(!pFeatureInfo)
		{
			return -1;
			return false;
		}

		return pFeatureInfo->m_iTimeOut;
	}

	/*
	 * This method reterives the number of days available for the license to expire for a feature
	 * This method will not checkout(consume) the license. It will simply check for the license.
	 * This is done by passing LM_CO_LOCALTEST flag to the lc_checkout() call.
	 */
	int Suite::GetAvailableDays(const char *sFeature,const char* sVersion,int &iNoOfDaysAvailable,char *sAvailabilityMsg)
	{
		Impl::FeatureInfo *pFeatureInfo=mpImpl->GetFeature(sFeature,sVersion);
		if(!pFeatureInfo)
		{
			iNoOfDaysAvailable = -1;
			sAvailabilityMsg = "";
			return 0;
		}

		iNoOfDaysAvailable = pFeatureInfo->m_iNoOfDaysAvailable;

		if(iNoOfDaysAvailable==LM_FOREVER)
			sprintf(sAvailabilityMsg,"%s has got Permanent License\n",sFeature);
		else if(iNoOfDaysAvailable>0)
			sprintf(sAvailabilityMsg,"%s license is available for another %d days\n",sFeature,iNoOfDaysAvailable);
		else if(iNoOfDaysAvailable==0)
			sprintf(sAvailabilityMsg,"%s license will expire at midnight today\n",sFeature);

		return 1;
	}
} } // namespaces License, Vct

