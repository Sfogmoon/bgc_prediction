import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC
from sklearn.feature_selection import VarianceThreshold


def feature_selection_var(train_matrix, test_matrix, var):
    sel = VarianceThreshold(threshold=var)
    sel.fit(train_matrix)
    train_matrix = sel.transform(train_matrix)
    test_matrix = sel.transform(test_matrix)
    return train_matrix, test_matrix


def select_features_correlation(train_matrix, threshold=1.0):
    features = []
    feature_matrix = np.transpose(train_matrix)
    correlations = np.corrcoef(feature_matrix)

    for i in range(len(correlations)):
        correlated = False
        for j in range(i):
            if correlations[i][j] >= threshold:
                correlated = True
        if not correlated:
            features.append(i)
    return features


def apply_feature_selections(matrix, features):
    feature_matrix = np.transpose(matrix)
    new_matrix = []
    for i in features:
        new_matrix.append(feature_matrix[i])
    return np.transpose(new_matrix)


def get_feature_maticies(sample_base, train_size):
    env_array = []

    sample = next(iter(sample_base.samples.values()))
    for env in sample.environments.keys():
        env_array.append(env)

    full_matrix = []
    for sample_name in sample_base.names:
        matrix_row = []
        sample = sample_base.samples[sample_name]
        for env in env_array:
            matrix_row.append(sample.environments[env])
        full_matrix.append(matrix_row)

    train_matrix = np.array(full_matrix[:train_size])
    test_matrix = np.array(full_matrix[train_size + 1:])

    # apply feature selection
    features = select_features_correlation(train_matrix, 0.99)
    train_matrix = apply_feature_selections(train_matrix, features)
    test_matrix = apply_feature_selections(test_matrix, features)
    train_matrix, test_matrix = feature_selection_var(train_matrix, test_matrix, 0.01)
    # train_matrix, test_matrix = normalize_features(train_matrix, test_matrix)
    return train_matrix, test_matrix


def normalize_features(train_matrix, test_matrix):
    feature_train = np.transpose(train_matrix.copy())
    feature_test = np.transpose(test_matrix.copy())
    for i in range(len(feature_train)):
        mean = np.mean(feature_train[i])
        std = np.std(feature_train[i])
        if std > 0:
            feature_train[i] = (feature_train[i] - mean) / std
            feature_test[i] = (feature_test[i] - mean) / std
        else:
            feature_train[i] = feature_train[i] * 0.0
            feature_test[i] = feature_test[i] * 0.0
    return np.transpose(feature_train), np.transpose(feature_test)


def extract_components(sample_base):
    train_size = int(len(sample_base.samples) * 0.75)
    train_matrix, test_matrix = get_feature_maticies(sample_base, train_size)
    train_norm, test_norm = normalize_features(train_matrix, test_matrix)
    # train_norm, test_norm = train_matrix, test_matrix

    # get y
    # target_names = ['Gut', 'Oral', 'Vaginal', 'Skin']
    # colors = ['navy', 'turquoise', 'darkorange', 'black']
    # stry = sample_base.info['STArea']

    # target_names = ['Underground', 'Open']
    # colors = ['navy', 'red']
    # stry = sample_base.info['Ground Level']
    target_names = ['Manhattan', 'Brooklyn', 'Bronx', 'Queens']
    colors = ['navy', 'turquoise', 'darkorange', 'black']
    stry = sample_base.info['Borough']
    # Chi2

    # target_names = ['Stool', 'Tongue_dorsum', 'Buccal_mucosa', 'Supragingival_plaque', 'Posterior_fornix', 'Anterior_nares']
    # colors = ['navy', 'turquoise', 'darkorange', 'black', 'red', 'darkgreen']
    # stry = sample_base.info['STSite']

    # target_names = ['Male', 'Female']
    # stry = sample_base.info['Gender']
    # colors = ['navy', 'darkorange']

    train_y = stry[:train_size]
    y = np.array(train_y)
    test_y = np.array(stry[train_size + 1:])

    print("Starting. Train sizes:", len(train_matrix), len(train_matrix[0]), "Test sizes:", len(test_matrix), len(test_matrix[0]))

    # pca
    pca = PCA(n_components=2)
    pca.fit(train_matrix)
    X_pca = pca.transform(train_matrix)
    print('PCA explained variance ratio (first two components): %s' % str(pca.explained_variance_ratio_))

    # pca norm
    pca2 = PCA(n_components=2)
    pca2.fit(train_norm)
    X_pca2 = pca.transform(train_norm)
    print('PCA norm explained variance ratio (first two components): %s' % str(pca2.explained_variance_ratio_))

    # svd
    svd = TruncatedSVD(n_components=2)
    svd.fit(train_norm)
    X_svd = svd.transform(train_norm)

    # latent dirichlet
    lda1 = LatentDirichletAllocation(n_components=3, max_iter=10, learning_method='batch', random_state=0)
    lda1.fit(train_matrix)
    X_lda1 = lda1.transform(train_matrix)

    # linear discriminant
    lda2 = LinearDiscriminantAnalysis(n_components=2)
    X_lda2 = lda2.fit(train_matrix, y).transform(train_matrix)
    X_lda3 = lda2.transform(test_matrix)
    predict_y3 = lda2.predict(test_matrix)
    print("LDA accuracy. True:", sum(predict_y3 == test_y), "All:", sum(elem in target_names for elem in test_y))

    # Naive Bayes
    clf = LinearSVC()
    clf.fit(train_matrix, y)
    predict_y4 = clf.predict(test_matrix)
    print("NB accuracy. True:", sum(predict_y4 == test_y), "All:", sum(elem in target_names for elem in test_y))

    # plots
    plt.figure()
    for color, i, target_name in zip(colors, target_names, target_names):
        plt.scatter(X_pca[y == i, 0], X_pca[y == i, 1], color=color, alpha=.6, s=5, lw=1,
                    label=target_name)
    plt.legend(loc='best', shadow=False, scatterpoints=1)
    plt.title('PCA of the data')

    plt.figure()
    for color, i, target_name in zip(colors, target_names, target_names):
        plt.scatter(X_pca2[y == i, 0], X_pca2[y == i, 1], color=color, alpha=.6, s=5, lw=1,
                    label=target_name)
    plt.legend(loc='best', shadow=False, scatterpoints=1)
    plt.title('PCA norm of the data')

    plt.figure()
    for color, i, target_name in zip(colors, target_names, target_names):
        plt.scatter(X_svd[y == i, 0], X_svd[y == i, 1], color=color, alpha=.6, s=5, lw=1,
                    label=target_name)
    plt.legend(loc='best', shadow=False, scatterpoints=1)
    plt.title('SVD of the data')

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for color, i, target_name in zip(colors, target_names, target_names):
        ax.scatter(1.0 - X_lda1[y == i, 0], X_lda1[y == i, 1], 1.0 - X_lda1[y == i, 2], color=color, alpha=.6, s=5, lw=1,
                   label=target_name)
    plt.legend(loc='best', shadow=False, scatterpoints=1)
    plt.title('Latent Dirichlet Allocation of the data')

    plt.figure()
    for color, i, target_name in zip(colors, target_names, target_names):
        plt.scatter(X_lda2[y == i, 0], X_lda2[y == i, 1], color=color, alpha=.6, s=5, lw=1,
                    label=target_name)
    plt.legend(loc='best', shadow=False, scatterpoints=1)
    plt.title('Linear Discriminant Analysis of train data')

    plt.figure()
    for color, i, target_name in zip(colors, target_names, target_names):
        plt.scatter(X_lda3[test_y == i, 0], X_lda3[test_y == i, 1], color=color, alpha=.6, s=5, lw=1,
                    label=target_name)
    plt.legend(loc='best', shadow=False, scatterpoints=1)
    plt.title('Linear Discriminant Analysis of test data')

    plt.show(block=True)
    plt.interactive(False)

    return float(sum(predict_y3 == test_y)) / sum(elem in target_names for elem in test_y), \
           float(sum(predict_y4 == test_y)) / sum(elem in target_names for elem in test_y)
