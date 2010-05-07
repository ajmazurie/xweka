/*
  Evaluate the capability of a given list of classifiers to handle a given
  dataset. Uses the weka.core.Capabilities class introduced in Weka 3.5.3
*/

//package lib;

import weka.core.Instances;
import weka.core.Capabilities;
import weka.classifiers.Classifier;

import java.io.*;
import java.util.ArrayList;

public class weka_capabilities
 {
  public static void main (String[] args)
   {
	String arff_filename = args[0];
	String[] classifiers = args[1].split(",");

	// Load the dataset
	Instances dataset = null;

	try
	 {
	  dataset = new Instances(new BufferedReader(new FileReader(arff_filename)));
	  dataset.setClassIndex(dataset.numAttributes() - 1);
	 }

	catch (Exception e)
	 {
	  System.exit(1);
	 }

	// Ask the classifiers to accept or reject this dataset
	StringBuffer results = new StringBuffer();

	for (String classifier_name: classifiers)
	 {
	  boolean is_compatible;

	  try
	   {
		Classifier classifier = (Classifier)Class.forName(classifier_name).newInstance();
		Capabilities capabilities = classifier.getCapabilities();

		is_compatible = capabilities.test(dataset);
	   }

      catch (Exception e)
	   {
		is_compatible = false;
	   }

	  if (is_compatible)
	    results.append("1");
	  else
	    results.append("0");
	 }

    System.out.println(results.toString());
   }
 }
