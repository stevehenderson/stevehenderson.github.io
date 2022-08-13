[Goolge Cloud Build](https://cloud.google.com/build/docs) is an amazing service and my favorite GCP service.

However, it can be hard to conceptualize what's happening inside the builder during its run.

You can actually run almost any linux script inside the builder.  We can use this
to create some commands that send some valuable debugging information to the build session/log:

<script src="https://gist.github.com/stevehenderson/9536e34d82e09c90b82bd2a77f90dfa0.js"></script>

If you drop this Build Step near the top of your `cloudbuild.yaml` you can see what's in the builder parent directory,
where you Dockerfile is, etc.

