import unittest
import perg

class TestPerg(unittest.TestCase):

    def testFilenamesearch(self):
        self.assertEqual(filenamesearch("/home/Tim.Zwart/SlowLogin/com.adobe.granite.auth.saml-0.2.4.jar#/com/adobe/granite/auth/saml/SamlAuthenticationHandler.class","SamlAuthenticationHandler.class", "SamlAuthenticationHandler"), True)

if '__name__' == '__main__':
    unittest.main()
