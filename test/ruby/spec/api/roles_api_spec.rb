=begin
#Conjur

#This is an API definition for CyberArk DAP (part of AAM) and Conjur OSS v10+. You can find out more at [Conjur](https://www.conjur.org/) and [AAM](https://www.cyberark.com/products/privileged-account-security-solution/application-access-manager/) pages.

The version of the OpenAPI document: 0.0.1
Contact: conj_maintainers@cyberark.com
Generated by: https://openapi-generator.tech
OpenAPI Generator version: 4.3.1

=end

require 'spec_helper'
require 'json'

# Unit tests for OpenapiClient::RolesApi
# Automatically generated by openapi-generator (https://openapi-generator.tech)
# Please update as you see appropriate
describe 'RolesApi' do
  before do
    # run before each test
    @api_instance = OpenapiClient::RolesApi.new
  end

  after do
    # run after each test
  end

  describe 'test an instance of RolesApi' do
    it 'should create an instance of RolesApi' do
      expect(@api_instance).to be_instance_of(OpenapiClient::RolesApi)
    end
  end

  # unit tests for get_role
  # Get role information
  # Gets detailed information about a specific role, including the role members.  If a role A is granted to a role B, then role A is said to have role B as a member. These relationships are described in the “members” portion of the returned JSON.  ##### Listing members  If &#x60;members&#x60; is provided, you will get the members of a role.  If a &#x60;kind&#x60; query parameter is given, narrows results to only resources of that kind.  If a &#x60;limit&#x60; is given, returns no more than that number of results. Providing an &#x60;offset&#x60; skips a number of resources before returning the rest. In addition, providing an &#x60;offset&#x60; will give limit a default value of 10 if none other is provided. These two parameters can be combined to page through results.  If the parameter &#x60;count&#x60; is true, returns only the number of items in the list.  ##### Text search  If the search parameter is provided, narrows results to those pertaining to the search query. Search works across resource IDs and the values of annotations. It weights results so that those with matching id or a matching value of an annotation called name appear first, then those with another matching annotation value, and finally those with a matching kind. 
  # @param account Organization account name
  # @param kind Type of resource
  # @param identifier ID of the role for which to get the information about
  # @param [Hash] opts the optional parameters
  # @option opts [Boolean] :members Comma-delimited, URL-encoded resource IDs of the variables.
  # @option opts [Integer] :offset When listing members, start at this item number.
  # @option opts [Integer] :limit When listing members, return up to this many results.
  # @option opts [Boolean] :count When listing members, if &#x60;true&#x60;, return only the count of members.
  # @return [Object]
  describe 'get_role test' do
    it 'should work' do
      # assertion here. ref: https://www.relishapp.com/rspec/rspec-expectations/docs/built-in-matchers
    end
  end

end
