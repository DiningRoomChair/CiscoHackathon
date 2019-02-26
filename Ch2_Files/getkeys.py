apikeys = open('APIKeys.txt', 'r')
apikeys.readline()

mapquest = apikeys.readline()[:-1]  # bloody windows line endings

apikeys.readline()
apikeys.readline()

teams = apikeys.readline()[:-1]

apikeys.readline()
apikeys.readline()

github = apikeys.readline()[:-1]

apikeys.close()