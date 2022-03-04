import conans, os, re, shutil
from os.path import exists, join
from .Utility import Utility

class ProfileManagement(object):
	'''
	Provides functionality for managing Conan profiles
	'''
	
	# Methods that apply to all Conan profiles, including those not generated by conan-ue4cli
	
	@staticmethod
	def conanProfileDir():
		'''
		Returns the path to the Conan profiles directory
		'''
		return join(conans.paths.get_conan_user_home(), '.conan', 'profiles')
	
	@staticmethod
	def conanProfileFile(profile):
		'''
		Resolves the path to the file for the specified Conan profile
		'''
		return join(ProfileManagement.conanProfileDir(), profile)
	
	@staticmethod
	def duplicateProfile(source, dest):
		'''
		Duplicates an existing Conan profile
		'''
		
		# Remove the destination profile if it already exists
		sourceProfile = ProfileManagement.conanProfileFile(source)
		destProfile = ProfileManagement.conanProfileFile(dest)
		if exists(destProfile):
			os.unlink(destProfile)
		
		# Perform the copy
		print('Copying the "{}" Conan profile into a new profile named "{}"...'.format(source, dest))
		shutil.copy2(sourceProfile, destProfile)
	
	@staticmethod
	def removeProfile(profile):
		'''
		Removes the specified Conan profile if it exists
		'''
		profileFile = ProfileManagement.conanProfileFile(profile)
		if exists(profileFile):
			os.unlink(profileFile)
	
	
	# Methods that apply only to Conan profiles generated by conan-ue4cli
	
	@staticmethod
	def genericProfile():
		'''
		Returns the name of the generic Conan profile that gets generated for backwards compatibility with legacy versions of conan-ue4cli
		'''
		return 'ue4'
	
	@staticmethod
	def listGeneratedProfiles(includeGeneric=True):
		'''
		Returns a list of the Conan profiles that conan-ue4cli has already generated
		'''
		
		# Retrieve the full list of Conan profiles
		output = Utility.capture(['conan', 'profile', 'list'])
		profiles = output.stdout.decode('utf-8').replace('\r\n', '\n').split('\n')
		
		# Filter the list to identify the profiles generated by conan-ue4cli
		filterRegex = re.compile('ue[0-9]+\\.[0-9]+-.+')
		profiles = list([
			profile for profile in profiles
			if (includeGeneric == True and profile == 'ue4') or filterRegex.match(profile) is not None
		])
		
		# If there are no generated profiles then the user needs to run profile generation
		if len(profiles) == 0:
			raise RuntimeError('No conan-ue4cli profiles detected! Please run `ue4 conan generate` to generate a profile.')
		
		return profiles
	
	@staticmethod
	def profileEngineVersion(profile):
		'''
		Retrieves the Unreal Engine version string for the specified Conan profile
		'''
		return ProfileManagement._profileValue(profile, 'env.UNREAL_ENGINE_VERSION')
	
	@staticmethod
	def profilePlatform(profile):
		'''
		Retrieves the Conan platform string for the specified Conan profile
		'''
		return ProfileManagement._profileValue(profile, 'settings.os')
	
	@staticmethod
	def profileForHostPlatform(manager):
		'''
		Returns the Conan profile name for the host system platform and the current Unreal Engine installation
		'''
		
		# Some platforms have an architecture suffix for their default architecture, whilst others do not
		defaultArch = {
			'Linux': 'x86_64-unknown-linux-gnu',
			'Mac': 'x86_64'
		}
		
		targetPlatform = manager.getPlatformIdentifier()
		archSuffix = '-{}'.format(defaultArch[targetPlatform]) if targetPlatform in defaultArch else ''
		return 'ue' + manager.getEngineVersion('short') + '-' + targetPlatform + archSuffix
	
	
	# "Private" methods
	
	@staticmethod
	def _profileValue(profile, key):
		'''
		Retrieves the value of the requested key from the specified Conan profile
		'''
		return Utility.capture(['conan', 'profile', 'get', key, profile]).stdout.decode('utf-8').strip()
