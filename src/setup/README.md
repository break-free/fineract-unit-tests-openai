Refer to the master https://github.com/break-free/fineract-unit-tests-openai/blob/fix_use-token-counters/README.adoc[`README.adoc`] file for additional details.

# Set Up

* Fedora (TODO: put in an anchor for Fedora portion of document)
* Windows (TODO: put in an anchor for Windows portion of document)

## Fedora OS

> **Warning**
> The toolbox build script in its current state will attempt to find files from the `/root/` directory and match them. If you do not git clone into this directory the container will be misconfigured and unfit for use.

1. Download the code from this repository from your root directory. Note this includes the test files under `training/tests`.
2. Get your OpenAI API key and add it to your environment.

   `$ export OPENAI_API_KEY=<YOUR_KEY>`
3. Enter the code repo directory and run the `toolbox` script. Note the requirement to add both your OPEN API key as well as an API secret.

   ```
   cd fineract-unit-tests-openai
   $build_fineract-unit-tests-openai_toolbox.sh
   $ toolbox enter fineract-unit-tests-openai
   ```

---

> **Warning**
> The windows portion of the documentation is not complete! Do not rely on it in its current state!

## Windows

> **Note**
> All Powershell terminal isntructions below should be used from an elevated prompt

1. Download the code from this repository. Note this includes the test files under `training/tests`.
2. Get your OpenAI API key and add it to your environment.

   ```
   $Env:OPENAI_API_KEY=<YOUR_KEY>
   ```
3. Install prerequisite software

   a. [Python 3.11](https://www.python.org/downloads/release/python-3111/)

   b. [Miniconda3](https://docs.conda.io/en/latest/miniconda.html)

   c. Chocolatey [per their instructions](https://chocolatey.org/install) -- this is a package manager that will make (ha!) it easier to install Make for Windows

   d. Make: 
   
         choco install make

   e. [CMake for Windows](https://cmake.org/download/)

   f. FAISS [per their instructions](https://github.com/bitsun/faiss/blob/master/INSTALL.md), which will also need:
      
      1. [a GCC compiler](https://jmeubank.github.io/tdm-gcc/) (*probably* want [this one?](https://github.com/jmeubank/tdm-gcc/releases/download/v10.3.0-tdm64-2/tdm64-gcc-10.3.0-2.exe))

      2. a BLAS implementation (recommend [this one?](https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl-download.html?operatingsystem=window&distributions=offline))

> **Warning**
> Be sure to git clone to a separate parent repo to avoid nested git repos.

4. Git clone the java_code_chunker from breakfree's github repo

   ```
   cd ..\; git clone https://github.com/facebookresearch/faiss.git
   ```
5. Install prerequisite Python modules

   ```
   pip install --upgrade -r setup/requirements.txt
   ```
